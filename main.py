"""
This file is a part of the source code for the KithscordBot.
This project has been licensed under the MIT license.
Copyright (c) 2021-present Kithare Organization

This file is the main file of the KithscordBot source. Running this
starts the bot
"""

import discord

import kithscord
from kithscord.common import bot


@bot.event
async def on_ready():
    """
    Startup routines when the bot starts
    """
    await kithscord.init()


@bot.event
async def on_message(msg: discord.Message):
    """
    This function is called for every message by user.
    """
    if msg.author.bot:
        return

    await kithscord.handle_message(msg)


@bot.event
async def on_message_delete(msg: discord.Message):
    """
    This function is called for every message deleted by user.
    """
    await kithscord.message_delete(msg)


@bot.event
async def on_message_edit(old: discord.Message, new: discord.Message):
    """
    This function is called for every message edited by user.
    """
    if new.author.bot:
        return

    await kithscord.message_edit(old, new)


if __name__ == "__main__":
    kithscord.run()
