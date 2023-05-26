from discord.ext import tasks, commands
from discord import app_commands
import discord
import petrify_logic
import sql_helpers as sql
import json
import helpers
import time
import asyncio
import logging
from random import randint
from typing import Literal
from typing import Optional

logger = logging.getLogger('gnb')

class Timelock_Cog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.timelock_check.start()

	def cog_unload(self):
		self.timelock_check.cancel()

	@tasks.loop(seconds=20.0)
	async def timelock_check(self):
		timelocked_members = await sql.get_timelocks()
		for member in timelocked_members:
			logger.debug('Checking timelocked member '+str(member['user_id'])+' on '+str(member['guild_id']))
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


class Petrify_Cog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.hybrid_command(description='Petrify a statue candidate')
	async def petrify(self, context: commands.Context, target_member: discord.Member):
		guild_settings = sql.get_settings(context.guild.id)
		statue_active_role = guild_settings['statue_role']
		statue_candidate_role = guild_settings['statue_candidate_role']
		statue_admin_role = guild_settings['statue_admin_role']

		# If user does not have admin
		if (context.author.get_role(statue_admin_role) is None):
			await context.send(f'{context.author.mention} does not have permission to turn {target_member.mention} to stone!')
			logger.debug(f'{context.author.display_name}::{context.author.id} fails admin check to petrify {target_member.display_name}::{target_member.id}')
		# If target is not statue candidate
		elif (target_member.get_role(statue_candidate_role) is None):
			await context.send(f'{target_member.mention} does not want to be petrified!')
			logger.debug(f'{target_member.display_name}::{target_member.id} is not petrified because they are not a candidate')
		# Else - petrify
		else:
			result = await petrify_logic.petrify(target_member, context.guild, petrify_logic.Reason.by_admin)
			await context.send(result)
			logger.debug(f'{context.author.display_name}::{context.author.id} petrifies {target_member.display_name}::{target_member.id}')

	@commands.hybrid_command(description='Unpetrify a statue candidate')
	async def unpetrify(self, context: commands.Context, target_member: discord.Member):
		guild_settings = sql.get_settings(context.guild.id)
		statue_active_role = guild_settings['statue_role']
		statue_candidate_role = guild_settings['statue_candidate_role']
		statue_admin_role = guild_settings['statue_admin_role']

		# If user is not statue
		if (target_member.get_role(statue_active_role) is None):
			await context.send(f'{target_member.mention} isn\'t petrified!')
			result = await petrify_logic.unpetrify(target_member, context.guild, petrify_logic.Reason.by_admin)
			logger.debug(f'{target_member.display_name}::{target_member.id} is not a statue')
		# If user does not have admin
		elif (context.author.get_role(statue_admin_role) is None):
			await context.send(f'{context.author.mention} does not have permission to revert {target_member.mention}!')
			logger.debug(f'{context.author.display_name}::{context.author.id} fails admin check to unpetrify {target_member.display_name}::{target_member.id}')
		# If target is not statue candidate
		elif (target_member.get_role(statue_candidate_role) is None):
			await context.send(f'{target_member.mention} is stone, but left the statue candidate role. I guess they don\'t want to be changed back!')
			logger.debug(f'{target_member.display_name}::{target_member.id} is not a candidate')
		# Else - unpetrify
		else:
			result = await petrify_logic.unpetrify(target_member, context.guild, petrify_logic.Reason.by_admin)
			logger.debug(f'{context.author.display_name}::{context.author.id} unpetrifies {target_member.display_name}::{target_member.id}')
			await context.send(result)


class Selfpetrify_Cog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	# Self-petrify
	@commands.hybrid_group(fallback='help')
	async def selfpetrify(self, context: commands.Context):
		if context.invoked_subcommand is None:
			await context.send('Missing parameter.\n \
- `toggle` to toggle self-petrify with free unpetrify\n \
- `chance <1-100> <interval>` to be petrified with a \% chance every interval \n \
- `date <date min> [date max]` to be petrified for `date min` (or a random amount up to `date-max` if provided)')

	@selfpetrify.command(description='Toggles self-petrification. Can be used freely.')
	async def toggle(self, context: commands.Context):
		guild_settings = sql.get_settings(context.guild.id)
		statue_active_role = guild_settings['statue_role']

		if (context.author.get_role(statue_active_role) is None):
			result = await petrify_logic.petrify(context.author, context.guild, petrify_logic.Reason.by_self_toggle)
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
	async def timelock(self, context: commands.Context, timemin: str, timemax: Optional[str]):
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
		elif timemin_conv > (60*24*7*3)+1 or timemax_conv > (60*60*24*7*4)+1:
			await context.send("Time cannot be greater than 4 weeks")
			return

		# Get a random time

		unlock_time = int(time.time()) + randint(timemin_conv,timemax_conv)

		result = await petrify_logic.petrify(context.author, context.guild, petrify_logic.Reason.by_self_time, unlock_time=unlock_time)
		await context.send(result)




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
		if (context.author.get_role(statue_admin_role) is not None):
			channel_list = await context.guild.fetch_channels()
			for channel in channel_list:
				try:
					await self.fix_channel_permissions(context, channel)
					logger.debug(f'updating channel perms for {channel.name}::{channel.id} on {context.guild.name}::{context.guild.id}')
				except Exception as err:
					logger.debug(f'could not update channel permissions for {channel.name}::{channel.id} on {context.guild.name}::{context.guild.id}')
					logger.debug(err)
			await context.send('Updated channel permissions.')

	# Fix server's channel permissions on channel creation
	@commands.Cog.listener()
	async def on_guild_channel_create(channel):
		await fix_channel_permissions(channel)

	async def fix_channel_permissions(self, context, channel):
		guild_settings = sql.get_settings(context.guild.id)
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

	@setup.command(name='channel')
	async def setup_channel(self, context: commands.Context, channel_type: Literal['statues_only'], action: Literal['add','remove'], channel: discord.TextChannel):
		guild_settings = sql.get_settings(context.guild.id)
		try:
			statue_only_channels = json.loads(guild_settings['statue_only_channels'])
		except: 
			statue_only_channels = []
		if action == 'add':
			statue_only_channels.append(channel.id)
			response = f'Added channel ID {channel.id} as statues only channel'
		else: 
			statue_only_channels.remove(channel.id)
			response = f'Removed channel ID {channel.id} as statues only channel - you\'ll need to clear the permissions manually.'
		sql.set_setting(context.guild.id,"statue_only_channels",f'"{json.dumps(statue_only_channels)}"')
		await context.send(response)

	# List of permissions
	possible_permissions = Literal['send_messages','view_channels','react','speak','stream','read_message_history','join_voice']
	@setup.command(name='permissions')
	async def setup_permissions(self, context: commands.Context, perm_type: possible_permissions, true_false: bool):
		sql.set_setting(context.guild.id,f'can_{perm_type}',int(true_false))
		await context.send(f'Set can_{perm_type} to {true_false}')

	# List of possible roles
	possible_roles = Literal['statue_admin','statue_candidate','statue','gorgon_candidate','gorgon']
	@setup.command(name='role')
	async def setup_role(self, context: commands.Context, role_type: possible_roles, role: discord.Role):
		sql.set_setting(context.guild.id,f'{role_type}_role',int(role.id))
		await context.send(f'Set {role_type}_role to {role.name} aka {role.id}')

	@setup.command(name='print')
	async def setup_print(self, context: commands.Context):
		guild_settings = sql.get_settings(context.guild.id)
		print_settings = ''
		for key in guild_settings:
			print_settings = f'{key}\t= {guild_settings[key]}'
		await context.send(print_settings)
