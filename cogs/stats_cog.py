from discord.ext import tasks, commands
#from discord import app_commands
import discord
#import petrify_logic
import sql_helpers as sql
#import json
import materials
#import helpers
#import time
#import logging
#from random import randint
#from random import choice
#from typing import Literal
from typing import Optional

logger = logging.getLogger('gnb')

class Status_Cog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.hybrid_command(aliases='inspect',description='Get the status of yourself or another member')
	async def status(self, context: commands.Context, target_member: Optional[discord.Member]):
		# Get guild settings
		# guild_settings = sql.get_settings(context.guild.id)

		# Account for people running the command w/o specifying someone, default to self
		if target_member is None:
			target_member = context.author

		logger.debug(f'Getting status info for {target_member.display_name}::{target_member.id} on {context.guild.name}::{context.guild.id}')

		# Get current status of target
		target_status = await sql.get_status(target_member.id, context.guild.id)

		# Craft embed
		embed = discord.Embed()

		if target_member.display_icon is not None:
			embed.set_author(target_member.display_name, icon_url=target_member.display_icon.url)
		else:
			embed.set_author(target_member.display_name)

		if target_status['status'] == sql.Status['unpetrified']
			embed.add_field(name='Material', value='None')
			embed.add_field(name='Status', value='Unpetrified')

		elif target_status['status'] == sql.Status['petrified_by_self_toggle']:
			embed.add_field(name='Material', value=materials.Material(target_status['material']).name)
			embed.add_field(name='Status', value='Self-tribute')
			embed.add_field(name='Petrified at', value=f'<t:{target_status["petrified_time"]}>', inline=False)

		elif target_status['status'] == sql.Status['petrified_by_self_time']:
			embed.add_field(name='Material', value=materials.Material(target_status['material']).name)
			embed.add_field(name='Status', value='Time-locked Tribute')
			embed.add_field(name='Petrified at', value=f'<t:{target_status["petrified_time"]}>', inline=False)
			embed.add_field(name='Tribute until', value=f'<t:{target_status["unlock_time"]}>', inline=False)
			embed.add_field(name='Tribute time remaining', value=f'<t:{target_status["unlock_time"]}>', inline=False)

		elif target_status['status'] == sql.Status['petrified_by_self_chance']:
			embed.add_field(name='Material', value=materials.Material(target_status['material']).name)
			embed.add_field(name='Status', value='Chance-locked Tribute')
			embed.add_field(name='Petrified at', value=f'<t:{target_status["petrified_time"]}>', inline=False)

		elif target_status['status'] == sql.Status['petrified_by_admin']:
			embed.add_field(name='Material', value=materials.Material(target_status['material']).name)
			embed.add_field(name='Status', value='Petrified by Priest ')
			embed.add_field(name='Petrified at', value=f'<t:{target_status["petrified_time"]}>', inline=False)

		context.send(content='Let\'s see what we have here...', embed=embed)

