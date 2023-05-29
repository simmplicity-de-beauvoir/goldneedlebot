import os
import discord
import petrify_logic
import time
import helpers
import sql_helpers
import logging
from typing import Optional
from random import randint

from discord.ext import tasks, commands
from discord import app_commands

# Cogs import
import cogs.admin_config
import cogs.admin_petrify
import cogs.self_petrify
import cogs.stats
import cogs.timelock

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='--', intents=intents)
logger = logging.getLogger('gnb')

@bot.event
async def on_ready():
	logger.info(f'Logged in as {bot.user} (ID: {bot.user.id})')
	logger.info('---------------------------------------------')
	await bot.add_cog(cogs.timelock.Timelock_Cog(bot))
	await bot.add_cog(cogs.admin_petrify.Petrify_Cog(bot))
	await bot.add_cog(cogs.self_petrify.Selfpetrify_Cog(bot))
	await bot.add_cog(cogs.admin_config.Admin_Cog(bot))
	await bot.add_cog(cogs.stats.Status_Cog(bot))

# add statue_candidate role
@bot.hybrid_command(aliases=['statuecandidateroletoggle','iconsenttobepetrified'],description='Give yourself the statue candidate role so admins can petrify you.')
async def iwanttobepetrified(context: commands.Context):
	candidate_role = context.guild.get_role(sql_helpers.get_settings(context.guild.id)['statue_candidate_role'])
	# cache check
	if candidate_role not in context.author.roles:
		await context.author.add_roles(candidate_role)
		await context.send('Welcome to my legion of followers.~', ephemeral=True)
		logger.debug('Added '+context.author.display_name+'::'+str(context.author.id)+' to '+candidate_role.name+'::'+str(candidate_role.id))
	else:
		await context.author.remove_roles(candidate_role)
		await context.send('Have you no love for your goddess?', ephemeral=True)
		logger.debug('Removed '+context.author.display_name+'::'+str(context.author.id)+' from '+candidate_role.name+'::'+str(candidate_role.id))


