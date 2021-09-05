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


async def get_perms(mem: Union[discord.Member, discord.User]):
    """
    Get a (has_eval, is_admin) pair
    """
    roles: set[int] = set()
    if common.guild is not None and (
        isinstance(mem, discord.User) or mem.guild.id != common.guild.id
    ):
        # User messaging from another non-primary server or DM, check perms
        # with main (primary) guild
        try:
            mem_server = await common.guild.fetch_member(mem.id)
        except discord.HTTPException:
            pass
        else:
            if mem_server is not None:
                roles.update(map(lambda x: x.id, mem_server.roles))

    if isinstance(mem, discord.Member):
        roles.update(map(lambda x: x.id, mem.roles))

    if common.EVAL_ROLE in roles:
        return True, True

    for role_id in roles:
        if role_id in common.ADMIN_ROLES:
            return False, True

    return False, False


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

    has_eval, is_admin = await get_perms(invoke_msg.author)
    cmd = (
        admin.AdminCommand(invoke_msg, response_msg)
        if is_admin
        else user.UserCommand(invoke_msg, response_msg)
    )
    cmd.has_eval = has_eval
    await cmd.handle_cmd()
    return response_msg
