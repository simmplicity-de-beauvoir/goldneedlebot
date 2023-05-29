import os
import logging

import discord

import petrify_logic
import goldneedle_bot

import configparser




config = configparser.ConfigParser()
config.read(os.path.dirname(__file__)+os.path.sep+'authentication.ini')

handler = logging.FileHandler(filename=os.path.dirname(__file__)+os.path.sep+'goldneedlebot.log',encoding='utf-8', mode='w')

# create logger just for GNB messages

gnb_handler = logging.StreamHandler()
gnb_logger = logging.getLogger('gnb')
gnb_logger.setLevel(logging.DEBUG)
gnb_logger.addHandler(gnb_handler)
gnb_logger.debug('Testing GNB handler')

goldneedle_bot.bot.run(config.get("authentication","token"), log_handler=handler)
