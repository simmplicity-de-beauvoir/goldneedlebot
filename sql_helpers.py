import sqlite3
import logging
from enum import IntEnum

logger = logging.getLogger('gnb')

class Status(IntEnum):
	unpetrified = 0
	petrified_by_self_toggle = 1
	petrified_by_self_time = 2
	petrified_by_self_chance = 3
	petrified_by_admin = 4

class Material(IntEnum):
	stone = 0	# Material TF
	marble = 1
	gold = 2
	metal = 3
	rubber = 4
	sand = 5
	glass = 6
	resin = 10	# Encasement
	wax = 11
	chocolate = 12
	timestop = 20	# Status change
	frozen = 21
	mannequin = 30	# Other TF
	doll = 31
	debug = 999	# DEBUG MODE

# setup DB connection
con = sqlite3.connect('goldneedle.db')
con.row_factory = sqlite3.Row
cur = con.cursor()

# Create user status table
cur.execute(' '
'CREATE TABLE IF NOT EXISTS '
'status('
'user_id INT, '
'guild_id INT, '
'status INT DEFAULT 0, '	# see Status enum
'petrified_time INT DEFAULT 0, '	# start of current petrification
'unlock_time INT DEFAULT -1, '	# time to be unlocked at/last check time
'unlock_chance INT DEFAULT -1, '	# chance value 1-99(%) to be released during check
'unlock_interval INT DEFAULT -1, '	# interval to check chance at
'material INT DEFAULT 0,'	# see Material enum
'owner_id INT DEFAULT -1'	# owner_id
');')


# get the status column of a member given their user_id and the guild_id
# return dict of response
async def get_status(user_id, guild_id):
	sql_statement = f'SELECT * FROM status WHERE user_id = {user_id} AND guild_id = {guild_id}'
	logger.debug(f'Running SQL statement: {sql_statement}')
	res = con.execute(sql_statement)
	row = res.fetchone()

	# if user/aspect is not in table
	if row is None:
		return None
	# if user is in table
	else:
		return row

# set status columns of a member given their user_id and the guild_id
# columns is a dict of column_name:value pairs
async def set_status(user_id, guild_id, columns):
	sql_statement = f'SELECT * FROM status WHERE user_id = {user_id} AND guild_id = {guild_id}'
	logger.debug(f'Running SQL statement: {sql_statement}')
	res = con.execute(sql_statement)
	row = res.fetchone()

	# if user is not in table
	if row is None:
		sql_statement_columns = ''
		sql_statement_values = ''
		for key in columns:
			sql_statement_columns += f'{key},'
			sql_statement_values += f'{columns[key]},'
		sql_statement_columns += 'user_id,guild_id'
		sql_statement_values += f'{user_id},{guild_id}'
		sql_statement = f'INSERT INTO status ({sql_statement_columns}) VALUES ({sql_statement_values});'
		logger.debug(f'Running SQL statement: {sql_statement}')
		con.execute(sql_statement)
	else:
		sql_statement = 'UPDATE status SET '
		for key in columns:
			sql_statement += f'{key} = {columns[key]}, '
		# extra null operation to reduct first-line logic
		sql_statement += f'user_id = {user_id} '
		sql_statement += f'WHERE user_id = {user_id} AND guild_id = {guild_id};'
		logger.debug(f'Running SQL statement: {sql_statement}')
		con.execute(sql_statement)
	# apply transaction to table
	con.commit()
	# return to know if it was successful or not
	return True

# get all members of all servers that are in a timelock
# return a list of rows containing (user_id,guild_id,unlock_time)
async def get_timelocks():
	res = con.execute(f'SELECT user_id,guild_id,unlock_time FROM status WHERE status = {Status.petrified_by_self_time};')
	return res.fetchall()

# get all members of all servers that are in a chance-based lock
# return a list of rows containing (user_id,guild_id,unlock_time,unlock_chance,unlock_interval)
async def get_chancelocks():
	res = con.execute(f'SELECT user_id,guild_id,unlock_time,unlock_chance,unlock_interval FROM status WHERE status = {Status.petrified_by_self_chance};')
	return res.fetchall()

# Create server settings table
cur.execute(''
'CREATE TABLE IF NOT EXISTS '
'settings('
'guild_id INT PRIMARY KEY, '
'statue_only_channels TEXT DEFAULT "[0]", ' # list of IDs stored as string, channels restricted to statues/admins
'ignore_perms_channels TEXT DEFAULT "[0]", ' # list of IDs stored as string, channels to ignore for fix_perms
'can_send_messages INT DEFAULT 0, '	# .send_messages + .send_messages_in_threads + .create_public_threads + .create_private_threads (text)
'can_view_channels INT DEFAULT 1, '	# .read_messages (text)
'can_react INT DEFAULT 1, '	# .add_reactions (text)
'can_speak INT DEFAULT 0, '	# .speak (VC)
'can_stream INT DEFAULT 1, '	# .stream (VC)
'can_read_message_history INT DEFAULT 1, ' # .read_message_history (text)
'can_join_voice INT DEFAULT 1, ' # .connect (VC)
'statue_admin_role INT DEFAULT 0, '	# roles ID, changes per server
'statue_candidate_role INT DEFAULT 0, '
'statue_role INT DEFAULT 0, '
'gorgon_candidate_role INT DEFAULT 0, '
'gorgon_role INT DEFAULT 0, '
'max_timelock_time INT DEFAULT 2419200, '	# maximum timelock time
'allow_simm_admin INT'
');')


# return the specified setting
def get_settings(guild_id):
	res = con.execute(f'SELECT * FROM settings WHERE guild_id = {guild_id};')
	row = res.fetchone()
	if row == None:
		return None
	else:
		return row

# return the specified setting
def set_setting(guild_id, setting_name, setting_value):
	logger.info(f'Setting {guild_id} {setting_name} to {setting_value}')
	sql_statement = f'INSERT INTO settings (guild_id,{setting_name}) ' + \
			f'VALUES ({guild_id},{setting_value}) ' + \
			f'ON CONFLICT(guild_id) ' + \
			f'DO UPDATE SET {setting_name}=excluded.{setting_name};'
	logger.debug(sql_statement)
	con.execute(sql_statement)
	con.commit()
	return True

