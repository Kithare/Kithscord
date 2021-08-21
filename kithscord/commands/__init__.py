"""
This file is a part of the source code for the KithscordBot.
This project has been licensed under the MIT license.
Copyright (c) 2021-present Kithare Organization

This file exports a handle function, to handle commands posted by the users
"""

from __future__ import annotations

import io
from typing import Union

import discord

from kithscord import common
from kithscord.commands import admin, user
from kithscord.utils import embed_utils


def is_admin(mem: Union[discord.Member, discord.User]):
    """
    Return whether a user is an admin user
    """

    if not isinstance(mem, discord.Member):
        return False

    for role in mem.roles:
        if role.id in common.ADMIN_ROLES:
            return True

    return False


async def handle(invoke_msg: discord.Message, response_msg: discord.Message = None):
    """
    Handle a kh! command posted by a user
    """
    if response_msg is None:
        response_msg = await embed_utils.send(
            invoke_msg.channel,
            title="Your command is being processed:",
            fields=(("\u2800", "`Loading...`", False),),
        )

    log_txt_file = None
    escaped_cmd_text = discord.utils.escape_markdown(invoke_msg.content)
    if len(escaped_cmd_text) > 2047:
        with io.StringIO(invoke_msg.content) as log_buffer:
            log_txt_file = discord.File(log_buffer, filename="command.txt")

    await common.log_channel.send(
        embed=embed_utils.create(
            title=f"Command invoked by {invoke_msg.author} / {invoke_msg.author.id}",
            description=escaped_cmd_text
            if len(escaped_cmd_text) <= 2047
            else escaped_cmd_text[:2044] + "...",
            fields=(
                (
                    "\u200b",
                    f"by {invoke_msg.author.mention}\n**[View Original]({invoke_msg.jump_url})**",
                    False,
                ),
            ),
        ),
        file=log_txt_file,
    )

    cmd = (
        admin.AdminCommand(invoke_msg, response_msg)
        if is_admin(invoke_msg.author)
        else user.UserCommand(invoke_msg, response_msg)
    )
    await cmd.handle_cmd()
    return response_msg
