"""
This file is a part of the source code for the KithscordBot.
This project has been licensed under the MIT license.
Copyright (c) 2021-present Kithare Organization

This file is the main file of kithscord subdir
"""

import io
import signal
import sys

import discord

from kithscord import commands, common, routine
from kithscord.utils import utils


async def _init():
    """
    Startup call helper for kithscord bot
    """
    sys.stdout = sys.stderr = common.stdout = io.StringIO()

    print("The KithscordBot is now online!")
    print("Server(s):")

    for server in common.bot.guilds:
        prim = ""

        if common.guild is None and server.id == common.ServerConstants.SERVER_ID:
            prim = "| Primary Guild"
            common.guild = server

        print(" -", server.name, "| Number of channels:", len(server.channels), prim)

        for channel in server.channels:
            if channel.id == common.ServerConstants.LOG_CHANNEL_ID:
                common.log_channel = channel
            elif channel.id == common.ServerConstants.CONSOLE_CHANNEL_ID:
                common.console_channel = channel


async def init():
    """
    Startup call helper for kithscord bot
    """
    try:
        await _init()
    except Exception:
        # error happened in the first init sequence. report error to stdout/stderr
        # note that the chances of this happening are pretty slim, but you never know
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        raise

    routine.handle_console.start()

    await utils.setup_kcr()
    if common.guild is None:
        raise RuntimeWarning(
            "Primary guild was not set. Some features of bot would not run as usual."
            " People running commands via DMs might face some problems"
        )


async def message_delete(msg: discord.Message):
    """
    This function is called for every message deleted by user.
    """
    if msg.id in common.cmd_logs:
        del common.cmd_logs[msg.id]

    elif msg.author.id == common.bot.user.id:
        for log, logmsg in common.cmd_logs.items():
            if logmsg.id == msg.id:
                del common.cmd_logs[log]
                return


async def message_edit(_: discord.Message, new: discord.Message):
    """
    This function is called for every message edited by user.
    """
    if not new.content.startswith(common.PREFIX):
        return

    try:
        if new.id in common.cmd_logs:
            await commands.handle(new, common.cmd_logs[new.id])
    except discord.HTTPException:
        pass


async def handle_message(msg: discord.Message):
    """
    Handle a message posted by user
    """
    if not msg.content.startswith(common.PREFIX):
        return

    ret = await commands.handle(msg)
    if ret is not None:
        common.cmd_logs[msg.id] = ret

    if len(common.cmd_logs) > 100:
        del common.cmd_logs[list(common.cmd_logs)[0]]


def cleanup(*_):
    """
    Call cleanup functions
    """
    common.bot.loop.run_until_complete(common.bot.close())
    common.bot.loop.close()


def run():
    """
    Does what discord.Client.run does, except, handles custom cleanup functions
    """
    # use signal.signal to setup SIGTERM signal handler, runs after event loop
    # closes
    signal.signal(signal.SIGTERM, cleanup)
    try:
        common.bot.loop.run_until_complete(common.bot.start(common.TOKEN))

    except KeyboardInterrupt:
        # Silence keyboard interrupt traceback (it contains no useful info)
        pass

    finally:
        cleanup()
