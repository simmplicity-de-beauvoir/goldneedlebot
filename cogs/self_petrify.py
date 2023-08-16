from discord.ext import tasks, commands
from discord import app_commands
import discord
import petrify_logic
import sql_helpers as sql
import json
import materials
import helpers
import time
import asyncio
import logging
from random import randint
from random import choice
from typing import Literal
from typing import Optional
from materials import valid_materials

logger = logging.getLogger('gnb')

class Selfpetrify_Cog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	# Self-petrify
	@commands.hybrid_group(fallback='help',aliases=['tribute','volunteer'])
	async def selfpetrify(self, context: commands.Context):
		if context.invoked_subcommand is None:
			await context.send("""Missing parameter.\n \
- `toggle [material]` to toggle self-petrify with free unpetrify\n \
- `timelock <timemin> [timemax] [material]` to be petrified for `timemin` seconds (or a random amount up to `timemax` if provided)""")
#- `chance <1-100> <interval>` to be petrified with a \% chance every interval \n \


	@selfpetrify.command(description='Toggles self-petrification. Can be undone with the same command.')
	async def toggle(self, context: commands.Context, material: valid_materials):

		# Error/default for material
		if material is None:
			material = 'stone'

		guild_settings = sql.get_settings(context.guild.id)
		statue_active_role = guild_settings['statue_role']

		if (context.author.get_role(statue_active_role) is None):
			result = await petrify_logic.petrify(context.author, context.guild, petrify_logic.Reason.by_self_toggle, material_str=material)
		else:
			result = await petrify_logic.unpetrify(context.author, context.guild, petrify_logic.Reason.by_self_toggle)
		await context.send(result)


	"""	
	@selfpetrify.command(description='Not yet implemented.')
	async def chance(self, context: commands.Context, datemin, datemax):
		statue_active_role = helpers.get_setting(context.guild.id,'statue_role')


		if (context.author.get_role(statue_active_role) is None):
			result = await petrify_logic.petrify(context.author, context.guild, petrify_logic.Reason.by_self_time, unlock_time=unlock_time)
		else:
			result = await petrify_logic.unpetrify(context.author, context.guild, petrify_logic.Reason.by_self_time)
		await context.send(result)
	"""
	@selfpetrify.command(description='Petrify yourself for a set (or random) period of time.')
	async def timelock(self, context: commands.Context, timemin: str, timemax: Optional[str], material: valid_materials):

		# Error/default for material
		if material is None:
			material = 'stone'

		timemin_conv = await helpers.timestr_to_num(timemin)
		if timemax == None:
			timemax_conv = timemin_conv
		else:
			timemax_conv = await helpers.timestr_to_num(timemax)

		# Check for invalid string
		if timemin_conv == None or timemax_conv == None:
			await context.send("Invalid time flag. Please provide seconds or with single-character unit suffix (i.e. `25d` for 25 days)")
			return

		# Check for greater than 4 week time
		elif timemin_conv > (60*60*24*7*3)+1 or timemax_conv > (60*60*24*7*4)+1:
			await context.send("Now, now, let's not petrify you for too long. I don't want you staying stiff for more than four weeks.")
			return

		# Get a random time
		if timemin_conv < timemax_conv:
			unlock_time = int(time.time()) + randint(timemin_conv,timemax_conv)
		# Account for randint range error when people put in numbers backwards
		else:
			unlock_time = int(time.time()) + randint(timemax_conv,timemin_conv)


		result = await petrify_logic.petrify(context.author, context.guild, petrify_logic.Reason.by_self_time, unlock_time=unlock_time, material_str=material)
		await context.send(result)




