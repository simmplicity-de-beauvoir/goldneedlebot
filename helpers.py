import time
import re

# convert date description into date
async def timestr_to_num(time_string):
	# check seconds value
	if time_string.isnumeric():
		return int(time_string)
	# check that string is valid
	if re.match(r'[0-9]+[mdw]',time_string) is None:
		return None
	if time_string.endswith('m'):
		return int(time_string.strip('m')) * 60
	if time_string.endswith('d'):
		return int(time_string.strip('d')) * 60 * 24
	if time_string.endswith('w'):
		return int(time_string.strip('w')) * 60 * 24 * 7

