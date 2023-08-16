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



class Safeword_Cog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_reaction_add(self, reaction, member: discord.Member):
		logger.info(reaction.emoji)
#		logger.info(reaction.emoji.name)
		# Is safeword?
		if reaction.emoji != '🆘':
			print(reaction.emoji == '🆘')
			return

		logger.info(f'{member.name} has safeworded.')

		guild_settings = sql.get_settings(member.guild.id)
		statue_active_role = guild_settings['statue_role']

		# Reset roles
		await member.remove_roles(member.guild.get_role(statue_active_role))
		await sql.set_status(member.id, member.guild.id, {'status':sql.Status.unpetrified})


