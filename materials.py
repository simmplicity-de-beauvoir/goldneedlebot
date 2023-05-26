# Helper functions to get formatted strings for different materials

import sqlite3
from enum import IntEnum
from sql_helpers import Material

"""
class Material(IntEnum):
	ston = 0	# Material TF
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
	debug = 999
"""
# setup DB connection
con = sqlite3.connect('materials_strings.db')
con.row_factory = sqlite3.Row
cur = con.cursor()

# Create user status table
cur.execute(''
	'CREATE TABLE IF NOT EXISTS '
	'material_strings('
	'material INT, '	# see Material enum
	'message_id TEXT, '	# message ID, describing the intent of the message (ex: admin petrifies candidate)
	'message_content TEXT'	# formatted string of the message
	');')

# get the status column of a member given their user_id and the guild_id
def get_string(material, message_id):
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
		sql_statement_values += '{user_id},{guild_id}'
		sql_statement = f'INSERT INTO status ({sql_statement_columns}) VALUES ({sql_statement_values});'
		logger.debug(f'Running SQL statement: {sql_statement}')
		con.execute(sql_statement)
	else:
		sql_statement = 'UPDATE status '
		for key in columns:
			sql_statement += f'{key} = {columns[key]}, '
		# extra null operation to reduct first-line logic
		sql_statement += f'user_id = {user_id}'
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


# settings schema
# guild_id INT PRIMARY KEY,
# statue_only_channel INT,
# can_speak INT,
# can_hear INT,
# can_react INT,
# statue_admin_role INT,
# statue_candidate_role INT,
# statue_role INT,
#allow_simm_admin INT

# return the specified setting
def get_settings(guild_id):
	res = con.execute(f'SELECT * FROM settings WHERE guild_id = {guild_id};')
	row = res.fetchone()
	if row == None:
		return None
	else:
		return row[setting_name]

# return the specified setting
def set_setting(guild_id, setting_name, setting_value):
	cur.execute(f'INSERT INTO settings (guild_id,{setting_name}) '
			'VALUES ({guild_id},{setting_value}) '
			'ON CONFLICT(guild_id) '
			'DO UPDATE SET {setting_name}=excluded.{setting_name};')
	con.commit()
	return True

# get the specified string for the specified material
def 

