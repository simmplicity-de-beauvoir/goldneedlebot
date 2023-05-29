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

class Admin_Cog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

# settings schema
# guild_id INT PRIMARY KEY,
# statue_only_channel INT,
# can_speak INT,
# can_hear INT,
# can_react INT,
# statue_admin_role INT,
# statue_candidate_role INT,
# statue_role INT,
#allow_simm_admin INT

	# Fix bot command sync
	@commands.command(description='Sync bot commands w/ server')
	async def sync(self, context: commands.Context):
		synced = await context.bot.tree.sync()
		await context.send(f'Sync\'d {len(synced)} commands to current guild.')

	# Fix permissions on all text channels
	@commands.hybrid_command(description='Fix channel permissions according to bot configuration.')
	async def fix_perms(self, context: commands.Context):
		guild_settings = sql.get_settings(context.guild.id)
		statue_admin_role = guild_settings['statue_admin_role']

		# If user does not have admin
		if (context.author.guild_permissions.manage_channels):
			channel_list = await context.guild.fetch_channels()
			ignore_perms_channels = json.loads(guild_settings['ignore_perms_channels'])
			for channel in channel_list:
				# Skip ignores
				if channel.id in ignore_perms_channels:
					logger.debug(f'skipping channel perms for {channel.name}::{channel.id} on {context.guild.name}::{context.guild.id}')
					continue

				# Fix perms on channel
				try:
					await self.fix_channel_permissions(context, channel, guild_settings)
					logger.debug(f'updating channel perms for {channel.name}::{channel.id} on {context.guild.name}::{context.guild.id}')
				except Exception as err:
					logger.debug(f'could not update channel permissions for {channel.name}::{channel.id} on {context.guild.name}::{context.guild.id}')
					logger.debug(err)
			await context.send('Updated channel permissions.')
		else:
			await context.send('Error: User must have manage_channels permission')

	# Fix server's channel permissions on channel creation
	#@commands.Cog.listener()
	#async def on_guild_channel_create(self, channel):
	#	await self.fix_channel_permissions(channel)

	async def fix_channel_permissions(self, context, channel, guild_settings):
		statue_only_channels = json.loads(guild_settings['statue_only_channels'])
		overwrites = discord.PermissionOverwrite()
		if channel.id in statue_only_channels:
			overwrites.send_messages = True
			overwrites.read_messages = True
			overwrites.view_channel = True
			overwrites.add_reactions = True
			await channel.set_permissions(channel.guild.get_member(self.bot.user.id), overwrite=overwrites)
			overwrites.send_messages = False
			overwrites.read_messages = False
			overwrites.view_channel = False
			overwrites.add_reactions = False
			await channel.set_permissions(channel.guild.default_role, overwrite=overwrites)
			overwrites.send_messages = True
			overwrites.read_messages = True
			overwrites.view_channel = True
			overwrites.add_reactions = True
			await channel.set_permissions(channel.guild.get_role(guild_settings["statue_role"]), overwrite=overwrites)
			overwrites.send_messages = True
			overwrites.read_messages = True
			overwrites.view_channel = True
			overwrites.add_reactions = True
			await channel.set_permissions(channel.guild.get_role(guild_settings["statue_admin_role"]), overwrite=overwrites)
			return
		if not guild_settings["can_send_messages"]:
			# Explicitly deny talking on the channel
			overwrites.send_messages = False
			overwrites.send_messages_in_threads = False
			overwrites.create_public_threads = False
			overwrites.create_private_threads = False
		if not guild_settings["can_view_channels"]:
			overwrites.read_messages = False
		if not guild_settings["can_react"]:
			overwrites.add_reactions = False
		if not guild_settings["can_speak"]:
			overwrites.speak = False
		if not guild_settings["can_stream"]:
			overwrites.stream = False
		if not guild_settings["can_read_message_history"]:
			overwrites.read_message_history = False
		if not guild_settings["can_join_voice"]:
			overwrites.connect = False
		# Apply changes
		print('yolo')
		await channel.set_permissions(channel.guild.get_role(guild_settings["statue_role"]), overwrite=overwrites)


	@commands.hybrid_group(fallback='help')
	async def setup(self, context: commands.Context):
		await context.send('''Configure bot options:
`/setup channel statues_only <channel_name>`: setup channel for "statues_only"
`/setup permissions *permission* (true|false)`: enable/disable permissions for statues
`/setup role (statue_admin|statue_candidate|statue) <role>`: setup roles associated with bot functions''')

	@setup.command(name='channel', description='select channels for channel-centered settings')
	async def setup_channel(self, context: commands.Context, channel_type: Literal['statue_only','ignore_perms'], action: Literal['add','remove'], channel: discord.TextChannel):
		if (context.author.guild_permissions.manage_channels):
			guild_settings = sql.get_settings(context.guild.id)
			try:
				existing_channels = json.loads(guild_settings[f'{channel_type}_channels'])
			except: 
				existing_channels = []
			if action == 'add':
				existing_channels.append(channel.id)
				response = f'Added channel ID {channel.id} as {channel_type} channel'
			else: 
				statue_only_channels.remove(channel.id)
				response = f'Removed channel ID {channel.id} as {channel_type} channel - you\'ll need to clear the permissions manually.'
			sql.set_setting(context.guild.id,"{channel_type}_channels",f'"{json.dumps(existing_channels)}"')
			await context.send(response)
		else:
			await context.send('Error: User must have manage_channels permission')

	# List of permissions
	possible_permissions = Literal['send_messages','view_channels','react','speak','stream','read_message_history','join_voice']
	@setup.command(name='permissions', description='set if statues can/can\'t do things')
	async def setup_permissions(self, context: commands.Context, perm_type: possible_permissions, true_false: bool):
		if (context.author.guild_permissions.manage_channels):
			sql.set_setting(context.guild.id,f'can_{perm_type}',int(true_false))
			await context.send(f'Set can_{perm_type} to {true_false}')
		else:
			await context.send('Error: User must have manage_channels permission')

	# List of possible roles
	possible_roles = Literal['statue_admin','statue_candidate','statue','gorgon_candidate','gorgon']
	@setup.command(name='role',description='select roles for various settings')
	async def setup_role(self, context: commands.Context, role_type: possible_roles, role: discord.Role):
		if (context.author.guild_permissions.manage_channels):
			sql.set_setting(context.guild.id,f'{role_type}_role',int(role.id))
			await context.send(f'Set {role_type}_role to {role.name} aka {role.id}')
		else:
			await context.send('Error: User must have manage_channels permission')

	@setup.command(name='print', description='print server\'s configuration')
	async def setup_print(self, context: commands.Context):
		if (context.author.guild_permissions.manage_channels):
			guild_settings = sql.get_settings(context.guild.id)
			print_settings = ''
			for key in guild_settings.keys():
				print_settings += f'{key}\t= {guild_settings[key]}\n'
			await context.send(print_settings)
		else:
			await context.send('Error: User must have manage_channels permission')
