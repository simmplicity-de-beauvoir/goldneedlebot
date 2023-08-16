# Helper functions to get formatted strings for different materials

import sqlite3
from enum import IntEnum
import csv
import os

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

# setup DB connection, create in next folder up
con = sqlite3.connect(os.path.join(os.path.dirname(__file__),'..','materials_strings.db'))
con.row_factory = sqlite3.Row
cur = con.cursor()

# delete existing table
sql_statement = 'DROP TABLE material_strings;'
res = con.execute(sql_statement)
con.commit()

# Create user status table
cur.execute(''
	'CREATE TABLE IF NOT EXISTS '
	'material_strings('
	'material INT, '	# see Material enum
	'message_id TEXT, '	# message ID, describing the intent of the message (ex: admin petrifies candidate)
	'message_content TEXT'	# formatted string of the message
	');')

supported_materials = ['debug','stone','timestop','resin','gold']

for mat in supported_materials:
	with open(f'dia_{mat}.csv', newline='') as csvfile:
	#	spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
		dialogue_csv = csv.reader(csvfile)
		for row in dialogue_csv:
			if row is None:
				continue
			material_val = Material[row[0]]
			sql_statement = f'INSERT INTO material_strings (material,message_id,message_content) VALUES ("{material_val}","{row[1]}","{row[2]}");'
			print(sql_statement)
			res = con.execute(sql_statement)
			con.commit()

print('Finished!')
