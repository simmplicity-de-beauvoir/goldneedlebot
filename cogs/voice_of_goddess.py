from discord.ext import tasks, commands
#from discord import app_commands
import discord
#import petrify_logic
import sql_helpers as sql
#import json
import materials
#import helpers
#import time
import logging
#from random import randint
#from random import choice
#from typing import Literal
from typing import Optional

logger = logging.getLogger('gnb')

class VoG_Cog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.hybrid_command(description='Speak as Pyralis')
	async def speak(self, context: commands.Context, *, message: str):

		logger.debug(f'{context.author.display_name} speaks as Pyralis: {message}')
		await context.channel.send(message)
		await context.send('confirmed',ephemeral=True,delete_after=0.1)
