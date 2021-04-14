import discord

import common
import user_commands
import admin_commands
from overload import *
import util


async def handle(cmd_str: str, invoker_msg: discord.Message, response_msg: discord.Message):
    args = cmd_str.split()
    arg_length = len(args) - 1
    log_msg = f"Command invoked by {invoker_msg.author} ({invoker_msg.author.id}): {cmd_str}"

    is_admin = False
    for role in invoker_msg.author.roles:
        if role.id in common.ADMIN_ROLES:
            is_admin = True
            break

    if arg_length == -1:
        return

    try:
        if is_admin and args[0] in admin_cmds:
            overloads = admin_cmds[args[0]]
            leng = -1 if -1 in overloads else arg_length if arg_length in overloads else -2

            if leng != -2:
                await overloads[leng](args[1:], invoker_msg, response_msg)
                await util.log(log_msg)
                return
        if args[0] in user_cmds:
            overloads = user_cmds[args[0]]
            leng = -1 if -1 in overloads else arg_length if arg_length in overloads else -2

            if leng != -2:
                await overloads[leng](args[1:], invoker_msg, response_msg)
                await util.log(log_msg)
                return
            else:
                await util.edit_embed(
                    response_msg,
                    "Incorrect amount of argument(s)!",
                    "",
                    0xFF0000
                )
        else:
            await util.edit_embed(
                response_msg,
                "Unrecognized command!",
                "",
                0xFF0000
            )

    except Exception as exc:
        await util.edit_embed(
            response_msg,
            "An exception occured while handling the command!",
            util.code_block(f"{type(exc).__name__}: {', '.join(map(str, exc.args))}"),
            0xFF0000
        )
