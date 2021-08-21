"""
This file is a part of the source code for the KithscordBot.
This project has been licensed under the MIT license.
Copyright (c) 2021-present Kithare Organization

This file defines the command handler class for the user commands of the bot
"""

from __future__ import annotations

import random
import re
from pathlib import Path

import discord
from kithscord import common
from kithscord.commands.base import BotException, CodeBlock, no_dm
from kithscord.utils import embed_utils, utils

from .base import BaseCommand


class UserCommand(BaseCommand):
    """Base class to handle user commands."""

    async def cmd_version(self):
        """
        ->type User commands
        ->signature kh!version
        ->description Get the version of the bot
        -----
        Implement kh!version, to report bot version
        """
        await embed_utils.replace(
            self.response_msg,
            title="Version",
            description=(
                f"Kithscord: `{common.__version__}`\n>>> {await utils.run_kcr('-v')}"
            ),
        )

    async def cmd_ping(self):
        """
        ->type User commands
        ->signature kh!ping
        ->description Get the ping of the bot
        -----
        Implement kh!ping, to get ping
        """
        timedelta = self.response_msg.created_at - self.invoke_msg.created_at
        sec = timedelta.total_seconds()
        sec2 = common.bot.latency  # This does not refresh that often
        if sec < sec2:
            sec2 = sec

        await embed_utils.replace(
            self.response_msg,
            title=random.choice(("Pingy Pongy", "Pong!")),
            description=f"The bot's ping is `{utils.format_time(sec, 0)}`\n"
            f"The Discord API latency is `{utils.format_time(sec2, 0)}`",
        )

    @no_dm
    async def cmd_help(self, *names: str):
        """
        ->type User commands
        ->signature kh!help [command]
        ->description Ask me for help
        ->example command kh!help help
        -----
        Implement kh!help, to display a help message
        """
        # needed for typecheckers to know that self.author is a member
        if isinstance(self.author, discord.User):
            return

        await embed_utils.send_help_message(
            self.response_msg,
            self.author,
            names,
            self.cmds_and_funcs,
            self.groups,
            self.page,
        )

    @no_dm
    async def cmd_refresh(self, msg: discord.Message):
        """
        ->type User commands
        ->signature kh!refresh <message>
        ->description Refresh a message which support pages.
        -----
        Implement kh!refresh, to refresh a message which supports pages
        """
        exc = BotException(
            "Message does not support pages",
            "The message specified does not support pages. Make sure you "
            "have replied to the correct message",
        )

        if (
            not msg.embeds
            or not msg.embeds[0].footer
            or not isinstance(msg.embeds[0].footer.text, str)
        ):
            raise exc

        data = msg.embeds[0].footer.text.splitlines()

        if len(data) != 3 and not data[2].startswith("Command: "):
            raise exc

        page_match = re.search(r"\d+", data[0])
        if page_match is None:
            raise exc

        page = page_match.group()
        cmd_str = data[2].replace("Command: ", "")

        if not page.isdigit() or not cmd_str:
            raise exc

        try:
            await self.response_msg.delete()
        except discord.errors.NotFound:
            pass

        # Handle the new command, the one that kh!refresh is trying to refresh
        self.response_msg = msg
        self.cmd_str = cmd_str
        self.page = int(page) - 1
        await self.handle_cmd()

    async def cmd_lex(self, code: CodeBlock):
        """
        ->type User commands
        ->signature kh!lex <code>
        ->description Get Kithare lexed output of Kithare code
        -----
        Implement kh!lex, to lex Kithare source
        """
        tempfile = Path("tempfile")
        tempfile.write_text(code.code, encoding="utf-8")

        try:
            await embed_utils.replace(
                self.response_msg,
                title="Lexed Kithare output",
                description=utils.code_block(
                    await utils.run_kcr(
                        "--tokens", "--timer", "--nocolor", str(tempfile)
                    )
                ),
            )
        finally:
            tempfile.unlink()

    async def cmd_parse(self, code: CodeBlock):
        """
        ->type User commands
        ->signature kh!parse <code>
        ->description Get Kithare parsed output of Kithare code
        -----
        Implement kh!parse, to parse Kithare source
        """
        tempfile = Path("tempfile")
        tempfile.write_text(code.code, encoding="utf-8")

        try:
            await embed_utils.replace(
                self.response_msg,
                title="Parsed Kithare output",
                description=utils.code_block(
                    await utils.run_kcr("--ast", "--timer", "--nocolor", str(tempfile))
                ),
            )
        finally:
            tempfile.unlink()
