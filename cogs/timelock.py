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

logger = logging.getLogger('gnb')

valid_materials = Optional[Literal['stone','debug','timestop']]

class Timelock_Cog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.timelock_check.start()

	def cog_unload(self):
		self.timelock_check.cancel()

	@tasks.loop(seconds=40.0)
	async def timelock_check(self):
		timelocked_members = await sql.get_timelocks()
		logger.debug(f'Checking timelocked members')
		for member in timelocked_members:
			unlock_member = False
			# if member's time is up
			if member['unlock_time'] <= time.time():
				logger.debug('Member '+str(member['user_id'])+' on '+str(member['guild_id'])+' is past their lockup time')
				unlock_member = True
			# error checking
			if member['unlock_time'] == -1:
				logger.debug('Member '+str(member['user_id'])+' on '+str(member['guild_id'])+' is has negative lockup time')
				unlock_member = True

			# unlock
			if unlock_member == True:
				# do some fancy stuff in case of cache issues
				guild_obj = self.bot.get_guild(member['user_id'])
				if guild_obj == None:
					guild_obj = await self.bot.fetch_guild(member['guild_id'])
				member_obj = guild_obj.get_member(member['user_id'])
				if member_obj == None:
					member_obj = await guild_obj.fetch_member(member['user_id'])

				logger.info(f"Time-unlocking {member_obj.id} aka {member_obj.display_name} from {guild_obj.name}")

				await petrify_logic.unpetrify(member_obj, guild_obj, petrify_logic.Reason.by_self_time)

	@timelock_check.before_loop
	async def before_timelock_check(self):
		logger.info('Waiting for bot before starting TimelockChecker cog ...')
		await self.bot.wait_until_ready()


