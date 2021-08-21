"""
This file is a part of the source code for the KithscordBot.
This project has been licensed under the MIT license.
Copyright (c) 2021-present Kithare Organization

This file exports the main AdminCommand class
"""

from __future__ import annotations

import os
import sys
import time

import discord
import psutil
from kithscord import common
from kithscord.commands.base import BotException, CodeBlock, String, add_group, no_dm
from kithscord.commands.user import UserCommand
from kithscord.utils import embed_utils, utils

process = psutil.Process(os.getpid())


class AdminCommand(UserCommand):
    """
    Base class for all admin commands
    """

    async def cmd_test_parser(self, *args, **kwargs):
        """
        ->type Admin commands
        ->signature kh!test_parser [*args] [**kwargs]
        ->description Test the arg parser on a custom input
        -----
        Implement kh!test_parser, for admins to test the parser
        """
        out = ""
        if args:
            out += "__**Args:**__\n"

        for cnt, arg in enumerate(args):
            if isinstance(arg, CodeBlock):
                out += f"{cnt} - Codeblock\n" + utils.code_block(
                    arg.code, code_type=arg.lang
                )
            elif isinstance(arg, String):
                out += (
                    f"{cnt} - String\n> " + "\n> ".join(arg.string.splitlines()) + "\n"
                )
            elif isinstance(arg, tuple):
                out += (
                    f"{cnt} - tuple\n {utils.code_block(repr(arg), code_type='py')}\n"
                )
            else:
                out += f"{cnt} - arg\n> {arg}\n"

        out += "\n"
        if kwargs:
            out += "__**Kwargs:**__\n\n"

        for name, arg in kwargs.items():
            if isinstance(arg, CodeBlock):
                out += f"{name} - Codeblock\n" + utils.code_block(
                    arg.code, code_type=arg.lang
                )
            elif isinstance(arg, String):
                out += (
                    f"{name} - String\n> " + "\n>".join(arg.string.splitlines()) + "\n"
                )
            elif isinstance(arg, tuple):
                out += (
                    f"{name} - tuple\n {utils.code_block(repr(arg), code_type='py')}\n"
                )
            else:
                out += f"{name} - arg\n> {arg}\n"

        out += "\n"
        await embed_utils.replace(
            self.response_msg,
            title="Here are the args and kwargs you passed",
            description=out,
        )

    async def cmd_heap(self):
        """
        ->type Admin commands
        ->signature kh!heap
        ->description Show the memory usage of the bot
        -----
        Implement kh!heap, for admins to check memory taken up by the bot
        """
        mem = process.memory_info().rss
        await embed_utils.replace(
            self.response_msg,
            title="Total memory used:",
            description=f"**{utils.format_byte(mem, 4)}**\n({mem} B)",
        )

    async def cmd_stop(self):
        """
        ->type Admin commands
        ->signature kh!stop
        ->description Stop the bot
        """
        await embed_utils.replace(
            self.response_msg,
            title="Stopping bot...",
            description="I gotta go now, but I will BRB, FINISH THE CEMENTER",
        )
        sys.exit(0)

    async def cmd_pull(self, branch: str = "main"):
        """
        ->type Admin commands
        ->signature kh!pull [branch]
        ->description Pull and install Kithare
        """
        await utils.pull_kithare(self.response_msg, branch)

    @add_group("sudo")
    async def cmd_sudo(self, msg: String):
        """
        ->type Admin commands
        ->signature pg!sudo [message]
        ->description Send a message trough the bot
        -----
        Implement pg!sudo, for admins to send messages via the bot
        """
        await self.invoke_msg.channel.send(msg.string)
        await self.response_msg.delete()
        await self.invoke_msg.delete()

    @add_group("sudo", "edit")
    async def cmd_sudo_edit(self, edit_msg: discord.Message, msg: String):
        """
        ->type Admin commands
        ->signature pg!sudo_edit [edit_message] [message string]
        ->description Edit a message that the bot sent.
        -----
        Implement pg!sudo_edit, for admins to edit messages via the bot
        """
        await edit_msg.edit(content=msg.string)
        await self.response_msg.delete()
        await self.invoke_msg.delete()

    @no_dm
    async def cmd_eval(self, code: CodeBlock, use_exec: bool = False):
        """
        ->type Admin commands
        ->signature pg!eval <command> [use_exec]
        ->description Execute arbitrary python code without restrictions
        -----
        Implement pg!eval, for admins to run arbitrary code on the bot
        """
        # make typecheckers happy
        if not isinstance(self.author, discord.Member):
            return

        if common.EVAL_ROLE not in map(lambda x: x.id, self.author.roles):
            raise BotException(
                "Insufficient permissions",
                "You do not have enough permissions to run this command.",
            )

        try:
            script_start = time.perf_counter()
            eval_output = exec(code.code) if use_exec else eval(code.code)
            total = time.perf_counter() - script_start

        except Exception as ex:
            raise BotException(
                "An exception occured:",
                utils.code_block(
                    type(ex).__name__ + ": " + ", ".join(map(str, ex.args))
                ),
            ) from None

        executed_time = f"Code executed in {utils.format_time(total)}"
        if eval_output is None:
            await embed_utils.replace(
                self.response_msg,
                title=executed_time,
            )
            return

        await embed_utils.replace(
            self.response_msg,
            title=f"Returned output ({executed_time}):",
            description=utils.code_block(repr(eval_output)),
        )


# monkey-patch admin command names into tuple
common.admin_commands = tuple(
    (
        i[len(common.CMD_FUNC_PREFIX) :]
        for i in dir(AdminCommand)
        if i.startswith(common.CMD_FUNC_PREFIX)
    )
)
