import sqlite3
from enum import IntEnum
# data type description
# user_id | guild_id | status | unlock_time | unlock_chance | unlock_interval
# int     | int      | int    | int         | int           | int
# unlock time is set date for unlock
# unlock chance is X/100 chance of unlock
# unlock interval is interval that unlock chance is run at

class Status(IntEnum):
	unpetrified = 0
	petrified_by_self_toggle = 1
	petrified_by_self_time = 2
	petrified_by_self_chance = 3
	petrified_by_admin = 4

# setup DB connection
con = sqlite3.connect('goldneedle.db')
con.row_factory = sqlite3.Row
cur = con.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS status(user_id INT, guild_id INT, status INT, unlock_time INT, unlock_chance INT, unlock_interval INT)')
cur.execute('CREATE TABLE IF NOT EXISTS settings(guild_id INT PRIMARY KEY,statue_only_channel INT,can_speak INT,can_hear INT,\
can_react INT,statue_admin_role INT,statue_candidate_role INT,statue_role INT,allow_simm_admin INT);')

# get the status of a member given their user_id and the guild_id
# return a tuple of the user's status
async def get_status(user_id, guild_id):
	res = con.execute(f'SELECT status,unlock_time,unlock_chance,unlock_interval FROM status WHERE user_id LIKE {user_id} AND guild_id LIKE {guild_id}')
	row = res.fetchone()

	# if user is not in table
	if row is None:
		return (Status.unpetrified,-1,-1,-1)
	# if user is in table
	else:
		return (row['status'], row['unlock_time'], row['unlock_chance'], row['unlock_interval'])

# set status of a member
async def set_status(user_id, guild_id, status, unlock_time = -1, unlock_chance = -1, unlock_interval = -1):
	res = con.execute(f'SELECT status,unlock_time,unlock_chance,unlock_interval FROM status WHERE user_id LIKE {user_id} AND guild_id LIKE {guild_id}')
	row = res.fetchone()

	# if user is not in table
	if row is None:
		cur.execute(f'INSERT INTO status VALUES ({user_id},{guild_id},{int(status)},{unlock_time},{unlock_chance},{unlock_interval})')
	else:
		cur.execute(f'UPDATE status SET status = {status}, unlock_time = {unlock_time}, unlock_chance = {unlock_chance}, unlock_interval = {unlock_interval} WHERE user_id = {user_id} AND guild_id = {guild_id}')
	# apply transaction to table
	con.commit()
	# return to know if it was successful or not
	return True

# get all members of all servers that are in a timelock
# return a list of rows containing (user_id,guild_id,unlock_time)
async def get_timelocks():
	res = con.execute(f'SELECT user_id,guild_id,unlock_time FROM status WHERE status LIKE {Status.petrified_by_self_time}')
	return res.fetchall()

# get all members of all servers that are in a chance-based lock
# return a list of rows containing (user_id,guild_id,unlock_time,unlock_chance,unlock_interval)
async def get_chancelocks():
	res = con.execute(f'SELECT user_id,guild_id,unlock_time,unlock_chance,unlock_interval FROM status WHERE status LIKE {Status.petrified_by_self_chance}')
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
def get_setting(guild_id, setting_name):
	res = con.execute(f'SELECT guild_id,{setting_name} FROM settings WHERE guild_id={guild_id}')
	row = res.fetchone()
	if row == None:
		return None
	else:
		return row[setting_name]

# return the specified setting
def set_setting(guild_id, setting_name, setting_value):
	cur.execute(f'INSERT INTO settings (guild_id,{setting_name}) \
			VALUES ({guild_id},{setting_value}) \
			ON CONFLICT(guild_id) \
			DO UPDATE SET {setting_name}=excluded.{setting_name}')
	con.commit()
	return True
