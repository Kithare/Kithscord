"""
This file is a part of the source code for the KithscordBot.
This project has been licensed under the MIT license.
Copyright (c) 2021-present Kithare Organization

This file defines the command handler class for the user commands of the bot
"""

from __future__ import annotations

import random
import re
import json
from pathlib import Path
from typing import Optional, Union

import discord
from googletrans import LANGUAGES, Translator
from kithscord import common
from kithscord.commands.base import BotException, CodeBlock, no_dm
from kithscord.utils import embed_utils, utils

from .base import BaseCommand, String, add_group

translator = Translator()

# dict of kcr commands with their descriptions
KCR_COMMANDS = {
    "version": "Shows `kcr` version",
    "lexicate": "Lexicate Kithare source to output tokens",
    "parse": "Parse Kithare source to generate AST",
}


def decode_lang(lang: str):
    """
    Decode lang string to a human readable format
    """
    try:
        return f"**{LANGUAGES[lang.lower()].capitalize()}** (`{lang}`)"
    except KeyError:
        return f"`{lang}` (unknown language code)"


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
            title="Kithscord Version",
            description=utils.code_block(common.__version__),
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
        command_str = data[2].replace("Command: ", "")

        if not page.isdigit() or not command_str:
            raise exc

        try:
            await self.response_msg.delete()
        except discord.errors.NotFound:
            pass

        # Handle the new command, the one that kh!refresh is trying to refresh
        self.response_msg = msg
        self.command_str = command_str
        self.page = int(page) - 1
        await self.handle_cmd()

    @add_group("kcr")
    async def cmd_kcr(self, *, _data: Optional[tuple[str, CodeBlock]] = None):
        """
        ->type User commands
        ->signature kh!kcr
        ->description Show a list of kithare commands
        """
        if _data is None:
            # show command list
            await embed_utils.replace(
                self.response_msg,
                title="Kithare Commands!",
                description="List of `kcr` commands Kithscord supports",
                fields=[(k, v, False) for k, v in KCR_COMMANDS.items()],
            )
            return

        command, code = _data
        if command not in KCR_COMMANDS:
            raise RuntimeError(f"{command} is not a valid kcr command.")

        if command == "version":
            # should never happen
            raise RuntimeError("version cannot be used with codeblock")

        # this tempfile is re-used for both code and output
        tempfile = Path(f"tempfile.{code.lang}" if code.lang else "tempfile")
        tempfile.write_text(code.code, encoding="utf-8")

        try:
            kcr_out = await utils.run_kcr(command, str(tempfile))

            content = f"`kcr` {command}d Output!"
            try:
                # formats kcr output and also checks it
                tempfile.write_text(json.dumps(json.loads(kcr_out), indent=2))
            except json.JSONDecodeError as e:
                # kcr spit invalid JSON. Could not format
                tempfile.write_bytes(kcr_out)
                content += (
                    "\n**THIS IS SUSSY**\n"
                    "This JSON is invalid according to the Python `json` module.\n"
                    f"Python Exception (`JSONDecodeError`): `{e}`\n"
                    "Could be a bug in Kithare (`kcr`)!\n"
                    "Sending unformatted output\n"
                )

            try:
                await self.invoke_msg.reply(
                    content=content,
                    file=discord.File(str(tempfile), filename="out.json"),
                )

                await self.response_msg.delete()
            except discord.HTTPException:
                pass

        finally:
            tempfile.unlink()

    @add_group("kcr", "version")
    async def cmd_kcr_version(self):
        """
        ->type User commands
        ->signature kh!kcr version
        ->description Get version of `kcr`
        """
        await embed_utils.replace(
            self.response_msg,
            title="`kcr` Version",
            description=utils.code_block(await utils.run_kcr("version", text=True)),
        )

    @add_group("kcr", "lexicate")
    async def cmd_kcr_lexicate(self, code: CodeBlock):
        """
        ->type User commands
        ->signature kh!kcr lexicate <code>
        ->description Get lexicated tokens from Kithare code
        """
        await self.cmd_kcr(_data=("lexicate", code))

    @add_group("kcr", "parse")
    async def cmd_kcr_parse(self, code: CodeBlock):
        """
        ->type User commands
        ->signature kh!kcr parse <code>
        ->description Get parsed AST output of Kithare code
        """
        await self.cmd_kcr(_data=("parse", code))

    @add_group("translate")
    async def cmd_translate(
        self,
        data: Union[String, discord.Message],
        dest: Union[str, String] = "en",
        src: Union[str, String] = "auto",
        extra_data: bool = False,
    ):
        """
        ->type User commands
        ->signature kh!translate <data> [src] [dest] [extra_data]
        ->description Translate a message or text using google translate
        ->extended description
        Here, `data` can be a string to translate, or a reference to a message to
        be translated. `src` is the source language, which is auto-detected by default
        and `dest` is the language to translate to, which is English by default. An
        additional boolean flag `extra_data` can be passed as `True` to get any extra
        (technical) data related to the translation
        -----
        Implement kh!translate, to translate data
        """
        text = data.content if isinstance(data, discord.Message) else data.string
        if not text:
            raise BotException(
                "Could not translate!",
                "Make sure to enter non-empty text for translation",
            )

        if isinstance(dest, String):
            dest = dest.string

        dest = dest.lower()
        if dest not in LANGUAGES:
            for lang, langname in LANGUAGES.items():
                if langname.lower().startswith(dest):
                    dest = lang
                    break
            else:
                raise BotException(
                    "Failed to translate text!",
                    f"`{dest}` is an unknown language name or code entered "
                    "for the argument `dest`!",
                )

        if isinstance(src, String):
            src = src.string

        src = src.lower()
        if src != "auto" and src not in LANGUAGES:
            for lang, langname in LANGUAGES.items():
                if langname.lower().startswith(src):
                    src = lang
                    break
            else:
                raise BotException(
                    "Failed to translate text!",
                    f"`{src}` is an unknown language name or code entered "
                    "for the argument `src`!",
                )

        translated = translator.translate(text, dest=dest, src=src)
        if not isinstance(translated.text, str) or not translated.text:
            raise BotException(
                "Could not translate!",
                "Failed to get a translation!",
            )

        desc = f"Successfully translated to {decode_lang(translated.dest)} "
        desc += "and the source was detected to be in " if src == "auto" else "from "
        desc += decode_lang(translated.src)

        fields: list[tuple[str, str, bool]] = [
            ("Translated text", utils.quotify(translated.text), False)
        ]

        pron: str = (
            translated.pronunciation
            if isinstance(translated.pronunciation, str)
            else ""
        )

        if pron:
            fields.append(("Pronunciation", utils.quotify(pron), False))

        try:
            origin_pron: str = translated.extra_data.pop("origin_pronunciation")
            if origin_pron:
                fields.append(
                    ("Pronunciation of source text", utils.quotify(origin_pron), False)
                )

        except KeyError:
            pass

        try:
            confidence = translated.extra_data.pop("confidence")
            if confidence is not None:
                fields.append(
                    (
                        "Translation confidence level",
                        utils.quotify(str(confidence)),
                        False,
                    )
                )

        except KeyError:
            pass

        if extra_data:
            fields.append(
                (
                    "Any extra (technical) data",
                    f"> `{translated.extra_data}`",
                    False,
                )
            )

        await embed_utils.replace(
            self.response_msg,
            title="Here is the translated text!",
            description=desc,
            fields=fields,
        )

    @no_dm
    @add_group("translate", "list")
    async def cmd_translate_list(self):
        """
        ->type User commands
        ->signature kh!translate list
        ->description Get the list of languages to which translations can be made
        """
        if not isinstance(self.author, discord.Member):
            # make typecheckers happy
            return

        embeds: list[discord.Embed] = []
        prev = 0
        languages = tuple(enumerate(LANGUAGES.items()))

        while prev <= len(languages):
            embeds.append(
                embed_utils.create(
                    title="Here is the list of languages",
                    description="\n".join(
                        f"**{i}.** {name.capitalize()} (`{lang}`)"
                        for i, (lang, name) in languages[prev : prev + 20]
                    ),
                )
            )
            prev += 20

        await embed_utils.PagedEmbed(
            self.response_msg,
            embeds,
            self.author,
            self.command_str,
            self.page,
        ).mainloop()
