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



class Petrify_Cog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.hybrid_command(description='Petrify a statue candidate')
	async def petrify(self, context: commands.Context, target_member: discord.Member, material: valid_materials):
		guild_settings = sql.get_settings(context.guild.id)
		statue_active_role = guild_settings['statue_role']
		statue_candidate_role = guild_settings['statue_candidate_role']
		statue_admin_role = guild_settings['statue_admin_role']
		target_status = await sql.get_status(target_member.id, context.guild.id)

		# Error/default for material
		if material is None:
			material = 'stone'
		material_val = sql.Material[material]

		if target_status is None:
			target_status = {}
			target_status['status'] = sql.Status.unpetrified

		# If user does not have admin
		if (context.author.get_role(statue_admin_role) is None):
			response = materials.get_string(material_val,"ERROR_PETRIFY_NOT_ADMIN").format(source=context.author, target=target_member)
			await context.send(response)
			logger.debug(f'{context.author.display_name}::{context.author.id} fails admin check to petrify {target_member.display_name}::{target_member.id}')
		# If target is not statue candidate
		elif (target_member.get_role(statue_candidate_role) is None):
			response = materials.get_string(material_val,"ERROR_PETRIFY_NOT_CANDIDATE").format(source=context.author, target=target_member)
			await context.send(response)
			logger.debug(f'{target_member.display_name}::{target_member.id} is not petrified because they are not a candidate')
		# Else - petrify
		else:
			result = await petrify_logic.petrify(target_member, context.guild, petrify_logic.Reason.by_admin, material_str=material, source=context.author)
			await context.send(result)
			logger.debug(f'{context.author.display_name}::{context.author.id} petrifies {target_member.display_name}::{target_member.id} using {material}')

	@commands.hybrid_command(description='Unpetrify a statue candidate')
	async def unpetrify(self, context: commands.Context, target_member: discord.Member):
		guild_settings = sql.get_settings(context.guild.id)
		statue_active_role = guild_settings['statue_role']
		statue_candidate_role = guild_settings['statue_candidate_role']
		statue_admin_role = guild_settings['statue_admin_role']
		target_status = await sql.get_status(target_member.id, context.guild.id)

		# error/default for target status
		if target_status is None:
			target_status = {}
			target_status['material'] = sql.Material['stone']

		# If user does not have admin
		if (context.author.get_role(statue_admin_role) is None):
			response = materials.get_string(target_status['material'],"ERROR_UNPETRIFY_NOT_ADMIN").format(source=context.author, target=target_member)
			await context.send(response)
			logger.debug(f'{context.author.display_name}::{context.author.id} fails admin check to unpetrify {target_member.display_name}::{target_member.id}')
		# If target is not statue candidate
		elif (target_member.get_role(statue_candidate_role) is None) and (target_member.get_role(statue_active_role) is not None):
			response = materials.get_string(target_status['material'],"ERROR_UNPETRIFY_NOT_CANDIDATE").format(source=context.author, target=target_member)
			logger.debug(f'{context.author.display_name} {target_status["material"]}')
			await context.send(response)
			logger.debug(f'{target_member.display_name}::{target_member.id} is not a candidate')
		# Else - unpetrify
		else:
			result = await petrify_logic.unpetrify(target_member, context.guild, petrify_logic.Reason.by_admin, source=context.author)
			logger.debug(f'{context.author.display_name}::{context.author.id} unpetrifies {target_member.display_name}::{target_member.id}')
			await context.send(result)


