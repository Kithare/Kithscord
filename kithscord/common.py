"""
This file is a part of the source code for the KithscordBot.
This project has been licensed under the MIT license.
Copyright (c) 2021-present Kithare Organization

This file defines some constants and variables used across the whole codebase
"""

import io
import os
from typing import Optional, Union

import discord

from dotenv import load_dotenv

__version__ = "v0.2"

if os.path.isfile(".env"):
    load_dotenv()  # take environment variables from .env


# declare type alias for any channel
Channel = Union[discord.TextChannel, discord.DMChannel, discord.GroupChannel]

bot = discord.Client()

TOKEN = os.environ["TOKEN"]

CMD_FUNC_PREFIX = "cmd_"

BASIC_MAX_FILE_SIZE = 8_000_000  # bytes

ZERO_SPACE = "\u200b"  # U+200B

PREFIX = "kh!"
cmd_logs: dict[int, discord.Message] = {}

# Kithare guild, or whichever is the 'primary' guild for the bot
guild: Optional[discord.Guild] = None

# IO object to redirect output to discord, gets patched later
stdout: Optional[io.StringIO] = None

# Tuple containing all admin commands, gets monkey-patched later
admin_commands: tuple[str, ...] = ()

log_channel: discord.TextChannel
console_channel: discord.TextChannel


class ServerConstants:
    """
    Class of all server constants. If you ever want to make a copy of the bot
    run on your own server on non-generic mode, replicate this class, but
    with the constants from your server
    """

    BOT_ID = 831731222543728690
    SERVER_ID = 810840019719684117

    LOG_CHANNEL_ID = 877784185933291580
    CONSOLE_CHANNEL_ID = 857641533129097246

    # Admin, Moderator, Contributor
    ADMIN_ROLES = {819457027776446494, 810843243071143946, 830567257272877126}


BOT_MENTION = f"<@!{ServerConstants.BOT_ID}>"

BOT_HELP_PROMPT = {
    "title": "Help",
    "color": 0xFFFF00,
    "description": f"""
Hey there, do you want to use {BOT_MENTION} ?
My command prefix is `{PREFIX}`.
If you want me to run your code, use Discord's code block syntax.
Learn more about Discord code formatting **[HERE](https://discord.com/channels/772505616680878080/774217896971730974/785510505728311306)**.
If you want to know about a specifc command run {PREFIX}help [command], for example {PREFIX}help exec.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━""",
}
