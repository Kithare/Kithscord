"""
This file is a part of the source code for the KithscordBot.
This project has been licensed under the MIT license.
Copyright (c) 2021-present Kithare Organization

This file defines some constants and variables used across the whole codebase
"""
from __future__ import annotations

import io
import os
from typing import Optional, Union

import discord

from dotenv import load_dotenv

__version__ = "v0.2.3"

if os.path.isfile(".env"):
    load_dotenv()  # take environment variables from .env

# declare type alias for any channel
Channel = Union[discord.TextChannel, discord.DMChannel, discord.GroupChannel]

bot = discord.Client()

TOKEN = os.environ["TOKEN"]
LOCAL_TEST = "LOCAL_TEST" in os.environ

CMD_FUNC_PREFIX = "cmd_"

BASIC_MAX_FILE_SIZE = 8_000_000  # bytes

ZERO_SPACE = "\u200b"  # U+200B

PREFIX = "kd!" if LOCAL_TEST else "kh!"

cmd_logs: dict[int, discord.Message] = {}

# Kithare guild, or whichever is the 'primary' guild for the bot
guild: Optional[discord.Guild] = None

# IO object to redirect output to discord, gets patched later
stdout: Optional[io.StringIO] = None

# Tuple containing all admin commands, gets monkey-patched later
admin_commands: tuple[str, ...] = ()

log_channel: discord.TextChannel
console_channel: discord.TextChannel

SERVER_ID = 810840019719684117

LOG_CHANNEL_ID = 877784185933291580
CONSOLE_CHANNEL_ID = 857641533129097246

# Discord ID of @Ankith and @Avaxar
# People whose IDs are in this list can run commands that 'eval/exec' along
# with having access to all admin commands of the bot
EVAL_MEMBERS = {763015391710281729, 414330602930700288}

# Administrator, Moderator and Lead Contributor
ADMIN_ROLES = {840365746676432956, 830567257272877126, 967717831233921024}

BOT_ID = 831731222543728690
BOT_MENTION = f"<@!{BOT_ID}>"

BOT_HELP_PROMPT = {
    "title": "Help",
    "color": 0xFFFF00,
    "description": f"""
Hey there, do you want to use {BOT_MENTION} ?
My command prefix is `{PREFIX}`.
If you want me to run your code, use Discord's code block syntax.
If you want to know about a specifc command run {PREFIX}help [command], for example {PREFIX}help exec.
???????????????????????????????????????????????????????????????????????????????????????????????????""",
}

# Channels where messages posted will be deleted (stuff like console channel)
NO_TALK_CHANNELS = {CONSOLE_CHANNEL_ID}
