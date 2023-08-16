# Helper functions to get formatted strings for different materials

import sqlite3
import typing
from random import choice
from enum import IntEnum
from typing import Optional
from typing import Literal

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
	debug = 999

valid_materials = Optional[Literal['stone','debug','timestop','resin']]

# setup DB connection
con = sqlite3.connect('materials_strings.db')
con.row_factory = sqlite3.Row
cur = con.cursor()

# Create message table, but it should already exist from import_dialogue.py
cur.execute(''
	'CREATE TABLE IF NOT EXISTS '
	'material_strings('
	'material INT, '	# see Material enum
	'message_id TEXT, '	# message ID, describing the intent of the message (ex: admin petrifies candidate)
	'message_content TEXT'	# formatted string of the message
	');')

# get the formatted string associated with a certain message
def get_string(material: int, message_id: str):
	sql_statement = f'SELECT * FROM material_strings WHERE material = "{material}" AND message_id = "{message_id}"'
#	print(f'Running SQL statement: {sql_statement}')
	res = con.execute(sql_statement)
	rows = res.fetchall()

	# if there are no messages assoicated with that material/message_id combo
	if rows == []:
		return "*stares silently while performing an action* ((this is a bug - some text hasn't been implemented! please message the dev!))"
	# select a random dialogue option
	else:
		return choice(rows)['message_content']
