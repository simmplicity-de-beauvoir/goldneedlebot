import sql_helpers
import logging
from time import ctime
from enum import IntEnum

logger = logging.getLogger('gnb')

# this matches up with the reasons in sql_helpers's Status
class Reason(IntEnum):
	by_self_toggle = 1
	by_self_time = 2
	by_self_chance = 3
	by_admin = 4

# return a string explaining if the action was successful
async def petrify(user, guild, reason, unlock_time = -1, unlock_chance = -1, unlock_interval = -1):
	guild_settings = sql_helpers.get_settings(guild.id)
	statue_active_role = guild_settings['statue_role']
	statue_candidate_role = guild_settings['statue_candidate_role']
	statue_admin_role = guild_settings['statue_admin_role']
	status = await sql_helpers.get_status(user.id, guild.id)

	if status == None:
		status = {}
		status['status'] = sql_helpers.Status.unpetrified

	petrify_success = False

	if status['status'] == sql_helpers.Status.unpetrified:
		# Create sql changes variable, reason == sql status enum
		changes = {'status':reason}

		if reason == Reason.by_admin:
			await sql_helpers.set_status(user.id, guild.id, changes)
			text = f"As you wish~ *touches {user.display_name}'s forehead, turning them to stone*"
			petrify_success = True
		elif reason == Reason.by_self_toggle:
			await sql_helpers.set_status(user.id, guild.id, changes)
			text = f"{user.display_name} petrifies themselves."
			petrify_success = True
		elif reason == Reason.by_self_time:
			changes['unlock_time'] = unlock_time
			await sql_helpers.set_status(user.id, guild.id, changes)
			text = f"{user.display_name} petrifies themselves until {ctime(unlock_time)}."
			petrify_success = True
		elif reason == Reason.by_self_chance:
			await sql_helpers.set_status(user.id, guild.id, changes)
			text = f"{user.display_name} has put their petrification into the hands of fate..."
			petrify_success = True
	elif status['status'] != sql_helpers.Status.petrified_by_admin and reason == Reason.by_admin:
		await sql_helpers.set_status(user.id, guild.id, {'status':sql_helpers.Status.petrified_by_admin})
		text = f"{user.display_name} is further petrified by anothers' magic and can no longer be freed by themselves, time, or chance."
		petrify_success = True
	else:
		text = f"{user.display_name} is unaffected. Perhaps they are already petrified by their own volition?"


	if petrify_success:
		# fix role
		await user.add_roles(guild.get_role(statue_active_role))
		# fix name
		if not (user.display_name.startswith('Petrified ')):
			try:
				await user.edit(nick='Petrified '+user.display_name)
			except Exception as err:
				logger.error(f"Error adding 'Petrified ' to name {user.display_name}")
				logger.error(err)
	return text


# return a string explaining if the action was successful, and the reason why/why-not
async def unpetrify(user, guild, reason):
	guild_settings = sql_helpers.get_settings(guild.id)
	statue_active_role = guild_settings['statue_role']
	statue_candidate_role = guild_settings['statue_candidate_role']
	statue_admin_role = guild_settings['statue_admin_role']
	status = await sql_helpers.get_status(user.id, guild.id)

	unpetrify_success = False
	if status['status'] == sql_helpers.Status.unpetrified:
		if (user.get_role(statue_active_role) is not None):
			text = "Mismatched petrification status. Depetrifying..."
			unpetrify_success = True
		# nothing to unpetrify
		else:
			pass
	elif status['status'] == sql_helpers.Status.petrified_by_admin:
		if reason != Reason.by_admin:
			text = "You cannot unpetrify yourself if petrified by an admin."
		else:
			await sql_helpers.set_status(user.id, guild.id, {'status':sql_helpers.Status.unpetrified})
			text = f"*giggles* Aww, already? But they looked so pretty...~ *snaps her fingers, reverting {user.display_name} to organic flesh and bone*"
			unpetrify_success = True
	elif status['status'] == sql_helpers.Status.petrified_by_self_toggle:
		if reason != Reason.by_self_toggle:
			text = "Self-petrified can only be unpetrified by themselves."
		else:
			await sql_helpers.set_status(user.id, guild.id, {'status':sql_helpers.Status.unpetrified})
			text = f"{user.display_name} chooses to stop being petrified."
			unpetrify_success = True
	elif status['status'] == sql_helpers.Status.petrified_by_self_time:
		if reason != Reason.by_self_time:
			text = f"{user.display_name} is petrified until their time runs out."
		else:
			await sql_helpers.set_status(user.id, guild.id, {'status':sql_helpers.Status.unpetrified})
			text = f"{user.display_name} is finally freed from their time-based prison."
			unpetrify_success = True
	elif status['status'] == sql_helpers.Status.petrified_by_self_chance:
		if reason != Reason.by_self_chance:
			text = f"{user.display_name} will only be free when luck smiles upon them."
		else:
			await sql_helpers.set_status(user.id, guild.id, {'status':sql_helpers.Status.unpetrified})
			text = f"{user.display_name} wins the luck of the draw and is freed."
			unpetrify_success = True

	## DEBUG MODE REMOVE LATER
#	if reason == Reason.by_admin:
#		unpetrify_success = True
#		await sql_helpers.set_status(user.id, guild.id, sql_helpers.Status.unpetrified)
#		text = f"{user.display_name} IS UNPETRIFIED FOR DEBUG REASONS."
	##########################

	if unpetrify_success:
		# fix role
		await user.remove_roles(guild.get_role(statue_active_role))
		# fix name
		if (user.nick is not None):
			try:
				await user.edit(nick=user.nick.removeprefix('Petrified '))
			except Exception as err:
				logger.error(f"Error removing 'Petrified ' to name {user.nick}")
				logger.error(err)
	return text
