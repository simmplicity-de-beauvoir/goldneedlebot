import sql_helpers as sql
import discord
import logging
import materials
import typing
from time import 
from enum import IntEnum

logger = logging.getLogger('gnb')

# this matches up with the reasons in sql_helpers's Status
class Reason(IntEnum):
	by_self_toggle = 1
	by_self_time = 2
	by_self_chance = 3
	by_admin = 4

# return a string explaining if the action was successful
async def petrify(target: discord.Member, guild: discord.Guild, reason, source: discord.Member = None , unlock_time = -1, unlock_chance = -1, unlock_interval = -1, material_str = 'stone'):
	guild_settings = sql.get_settings(guild.id)
	statue_active_role = guild_settings['statue_role']
	statue_candidate_role = guild_settings['statue_candidate_role']
	statue_admin_role = guild_settings['statue_admin_role']
	status = await sql.get_status(target.id, guild.id)
	material_val = sql.Material[material_str]

	if status == None:
		status = {}
		status['status'] = sql.Status.unpetrified

	petrify_success = False

	if status['status'] == sql.Status.unpetrified:
		# Create sql changes variable, reason == sql status enum
		changes = {'status':reason, 'material':material_val, 'petrified_time':time.time()}

		if reason == Reason.by_admin:
			await sql.set_status(target.id, guild.id, changes)
			text = materials.get_string(material_val,"PETRIFY_ADMIN").format(target=target, source=source)
			petrify_success = True
		elif reason == Reason.by_self_toggle:
			await sql.set_status(target.id, guild.id, changes)
			text = materials.get_string(material_val,"PETRIFY_SELF_TOGGLE").format(target=target)
			petrify_success = True
		elif reason == Reason.by_self_time:
			changes['unlock_time'] = unlock_time
			await sql.set_status(target.id, guild.id, changes)
			text = materials.get_string(material_val,"PETRIFY_SELF_TIME").format(target=target, time=unlock_time)
			petrify_success = True
		elif reason == Reason.by_self_chance:
			await sql.set_status(target.id, guild.id, changes)
			text = materials.get_string(material_val,"PETRIFY_SELF_CHANCE").format(target=target, chance=unlock_chance, interval=unlock_interval)
			petrify_success = True
	elif status['status'] != sql.Status.petrified_by_admin and reason == Reason.by_admin:
		await sql.set_status(target.id, guild.id, {'status':sql.Status.petrified_by_admin, 'material':material_val})
		text = materials.get_string(material_val,"PETRIFY_ADMIN_OVERWRITE").format(target=target, source=source)
		petrify_success = True
	else:
		text = materials.get_string(material_val,"ERROR_ALREADY_PETRIFIED").format(target=target)


	if petrify_success:
		# fix role
		await target.add_roles(guild.get_role(statue_active_role))
		# fix name
		prefix_text = materials.get_string(material_val,"NICKNAME_PREFIX").format()
		if not (target.display_name.startswith(prefix_text)):
			try:
				await target.edit(nick=prefix_text+target.display_name)
			except Exception as err:
				logger.error(f"Error adding '{prefix_text}' to name {target.display_name}")
				logger.error(err)
	return text


# return a string explaining if the action was successful, and the reason why/why-not
async def unpetrify(target: discord.Member, guild, reason, source: discord.Member = None):
	guild_settings = sql.get_settings(guild.id)
	statue_active_role = guild_settings['statue_role']
	statue_candidate_role = guild_settings['statue_candidate_role']
	statue_admin_role = guild_settings['statue_admin_role']
	status = await sql.get_status(target.id, guild.id)

	if status == None:
		status = {}
		status['status'] = sql.Status.unpetrified
		status['material'] = sql.Material['stone']

	unpetrify_success = False
	if status['status'] == sql.Status.unpetrified:
		if (target.get_role(statue_active_role) is not None):
			text = materials.get_string(status['material'],"ERROR_STATUS_MISMATCH").format(target=target)
			unpetrify_success = True
		# nothing to unpetrify
		else:
			text = materials.get_string(status['material'],"ERROR_ALREADY_UNPETRIFIED").format(target=target)
	elif status['status'] == sql.Status.petrified_by_admin:
		if reason != Reason.by_admin:
			text = materials.get_string(status['material'],"ERROR_UNPETRIFY_BY_SELF_WHEN_ADMIN_LOCKED").format(target=target)
		else:
			await sql.set_status(target.id, guild.id, {'status':sql.Status.unpetrified})
			text = materials.get_string(status['material'],"UNPETRIFY_ADMIN").format(target=target,source=source)
			unpetrify_success = True
	elif status['status'] == sql.Status.petrified_by_self_toggle:
		if reason != Reason.by_self_toggle:
			text = materials.get_string(status['material'],"ERROR_UNPETRIFY_GENERIC").format(target=target)
		else:
			await sql.set_status(target.id, guild.id, {'status':sql.Status.unpetrified})
			text = materials.get_string(status['material'],"UNPETRIFY_SELF_TOGGLE").format(target=target)
			unpetrify_success = True
	elif status['status'] == sql.Status.petrified_by_self_time:
		if reason != Reason.by_self_time:
			text = materials.get_string(status['material'],"ERROR_UNPETRIFY_GENERIC").format(target=target)
		else:
			await sql.set_status(target.id, guild.id, {'status':sql.Status.unpetrified})
			text = materials.get_string(status['material'],"UNPETRIFY_SELF_TIME").format(target=target)
			unpetrify_success = True
	elif status['status'] == sql.Status.petrified_by_self_chance:
		if reason != Reason.by_self_chance:
			text = materials.get_string(status['material'],"ERROR_UNPETRIFY_GENERIC").format(target=target)
		else:
			await sql.set_status(target.id, guild.id, {'status':sql.Status.unpetrified})
			text = materials.get_string(status['material'],"UNPETRIFY_SELF_CHANCE").format(target=target)
			unpetrify_success = True

	## DEBUG MODE REMOVE LATER
#	if reason == Reason.by_admin:
#		unpetrify_success = True
#		await sql.set_status(target.id, guild.id, sql.Status.unpetrified)
#		text = f"{target.display_name} IS UNPETRIFIED FOR DEBUG REASONS."
	##########################

	if unpetrify_success:
		# fix role
		await target.remove_roles(guild.get_role(statue_active_role))
		# fix name
		prefix_text = materials.get_string(status['material'],"NICKNAME_PREFIX").format()
		if (target.nick is not None):
			try:
				await target.edit(nick=target.nick.removeprefix(prefix_text))
			except Exception as err:
				logger.error(f"Error removing '{prefix_text}' to name {target.nick}")
				logger.error(err)
	return text
