"""
This file is a part of the source code for the KithscordBot.
This project has been licensed under the MIT license.
Copyright (c) 2021-present Kithare Organization

This file defines a "handle_console" function, that handles console redirects
to discord
"""

import io
import os
import sys

from discord.ext import tasks

from kithscord import common
from kithscord.utils import utils


@tasks.loop(seconds=5)
async def handle_console():
    """
    Function for sending the console output to the bot-console channel.
    """
    if common.stdout is None:
        return

    contents = common.stdout.getvalue()
    sys.stdout = sys.stderr = common.stdout = io.StringIO()

    # hide path data
    contents = contents.replace(os.getcwd(), "kithscord")
    if os.name == "nt":
        contents = contents.replace(os.path.dirname(sys.executable), "Python")

    if common.console_channel is None:
        # just print error to shell if we cannot sent it on discord
        print(contents, file=sys.__stdout__)
        return

    # the actual message limit is 2000. But since the message is sent with
    # code ticks, we need room for those, so 1980
    for content in utils.split_long_message(contents, 1980):
        content = content.strip()
        if not content:
            continue

        await common.console_channel.send(
            content=utils.code_block(content, code_type="cmd")
        )
