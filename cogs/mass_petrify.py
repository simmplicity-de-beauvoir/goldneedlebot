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

class MassPetrify_Cog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.hybrid_command(description='Debug to unpetrify everyone.')
	async def mass_unpetrify(self, context: commands.Context):
		if str(context.author.id) == '1066790754393010196':
			await context.send('Did you really think I\'d let you do that, Lyn?')
		elif str(context.author.id) not in ['566033105664868353','352264281896517635','1053028780383424563']:
			await context.send('No')
		else:
			await context.send('Commencing mass unpetrification in 10 seconds...')
