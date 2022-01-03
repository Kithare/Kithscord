"""
This file is a part of the source code for the KithscordBot.
This project has been licensed under the MIT license.
Copyright (c) 2021-present Kithare Organization

This file exports the main AdminCommand class
"""

from __future__ import annotations

import os
import subprocess
import sys
import time

import discord
import psutil
from kithscord import common
from kithscord.commands.base import BotException, CodeBlock, String, add_group
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

    async def cmd_stop(self, no_restart: bool = False):
        """
        ->type Admin commands
        ->signature kh!stop [no_restart]
        ->description Stop the bot. If no_restart is True, returns non-zero exit code
        """
        await embed_utils.replace(
            self.response_msg,
            title="Stopping bot..." if no_restart else "Restarting bot...",
            description=(
                "FINISH THE CEMENTER! My final message, goodbye!"
                if no_restart
                else "I'mma BRB, FINISH THE CEMENTER"
            ),
        )
        sys.exit(int(no_restart))

    @add_group("pull")
    async def cmd_pull(self):
        """
        ->type Admin commands
        ->signature kh!pull
        ->description Pull Kithare binaries AND pull kithscord
        """
        await self.cmd_pull_kithare()
        await self.cmd_pull_kithscord()

    @add_group("pull", "kithare")
    async def cmd_pull_kithare(self, branch: str = "main"):
        """
        ->type Admin commands
        ->signature kh!pull kithare [branch]
        ->description Pull and install Kithare
        """
        await utils.pull_kithare(self.response_msg, branch)

    @add_group("pull", "kithscord")
    async def cmd_pull_kithscord(
        self, branch: str = "main", reset_flag: str = "--hard", show_log: bool = False
    ):
        """
        ->type Admin commands
        ->signature kh!pull kithscord [branch] [reset_flag] [show_log]
        ->description Pull (git reset) Kithscord from git remote
        """
        if common.LOCAL_TEST:
            raise BotException(
                "Kithare cannot be pulled!",
                "On local botdev setup, pulling kithscord has been blocked "
                "for *obvious* reasons *duh*",
            )

        return_text = ""
        for command in (
            ("fetch",),
            ("checkout", branch),
            ("reset", reset_flag, f"origin/{branch}"),
        ):
            ret = subprocess.run(
                ("git", *command),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
            )

            return_text += ret.stdout + "\n"
            if ret.returncode:
                raise BotException(
                    "Kithscord pull failed!",
                    f"Process exited with exitcode {ret.returncode}!\n"
                    "Here is the full log:\n" + utils.code_block(return_text),
                )

        if show_log:
            await self.invoke_msg.reply(
                content="Kithscord pull was successful! Here is the log\n"
                + utils.code_block(return_text, 1900),
            )

        await self.cmd_stop()

    @add_group("sudo")
    async def cmd_sudo(self, msg: String):
        """
        ->type Admin commands
        ->signature kh!sudo <msg>
        ->description Send a message through the bot
        -----
        Implement kh!sudo, for admins to send messages via the bot
        """
        await self.invoke_msg.channel.send(msg.string)
        await self.response_msg.delete()
        try:
            await self.invoke_msg.delete()
        except discord.HTTPException:
            pass

    @add_group("sudo", "edit")
    async def cmd_sudo_edit(self, edit_msg: discord.Message, msg: String):
        """
        ->type Admin commands
        ->signature kh!sudo edit <edit_msg> <msg>
        ->description Edit a message that the bot sent.
        -----
        Implement kh!sudo edit, for admins to edit messages via the bot
        """
        try:
            await edit_msg.edit(content=msg.string)
        except discord.HTTPException:
            raise BotException(
                "Failed to edit message!",
                "You cannot edit messages sent by others!",
            )

        await self.response_msg.delete()
        try:
            await self.invoke_msg.delete()
        except discord.HTTPException:
            pass

    @add_group("sudo", "delete")
    async def cmd_sudo_delete(self, msg: discord.Message):
        """
        ->type Admin commands
        ->signature kh!sudo delete <msg>
        ->description Delete a message through the bot
        -----
        Implement kh!sudo delete, for admins to delete messages via the bot
        """
        try:
            await msg.delete()
        except discord.HTTPException:
            raise BotException(
                "Failed to delete message!",
                "This is probably due to missing perms to delete others messages",
            )

        await self.response_msg.delete()
        try:
            await self.invoke_msg.delete()
        except discord.HTTPException:
            pass

    async def cmd_eval(self, code: CodeBlock, use_exec: bool = False):
        """
        ->type Admin commands
        ->signature kh!eval <command> [use_exec]
        ->description Execute arbitrary python code without restrictions
        -----
        Implement kh!eval, for admins to run arbitrary code on the bot
        """
        if not self.has_eval:
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
