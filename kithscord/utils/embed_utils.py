"""
This file is a part of the source code for the KithscordBot.
This project has been licensed under the MIT license.
Copyright (c) 2021-present Kithare Organization

This file defines some important embed related utility functions.
"""

from __future__ import annotations

import asyncio
import datetime
import re
import typing
from typing import Iterable, Optional, Union

import discord
from discord.embeds import EmptyEmbed
from kithscord import common
from kithscord.commands.parser import BotException

DEFAULT_EMBED_COLOR = 0xFF8C00

# regex for doc string
regex = re.compile(
    # If you add a new "section" to this regex dont forget the "|" at the end
    # Does not have to be in the same order in the docs as in here.
    r"(->type|"
    r"->signature|"
    r"->description|"
    r"->example command|"
    r"->extended description\n|"
    r"\Z)|(((?!->).|\n)*)"
)


def create(
    author_name: Optional[str] = EmptyEmbed,
    author_url: Optional[str] = EmptyEmbed,
    author_icon_url: Optional[str] = EmptyEmbed,
    title: Optional[str] = EmptyEmbed,
    url: Optional[str] = EmptyEmbed,
    thumbnail_url: Optional[str] = EmptyEmbed,
    description: Optional[str] = EmptyEmbed,
    image_url: Optional[str] = EmptyEmbed,
    color: int = DEFAULT_EMBED_COLOR,
    fields: Union[list, tuple] = (),
    footer_text: Optional[str] = EmptyEmbed,
    footer_icon_url: Optional[str] = EmptyEmbed,
    timestamp: Optional[Union[str, datetime.datetime]] = EmptyEmbed,
):
    """
    Creates an embed with a much more tight function.
    """
    embed = discord.Embed(
        title=title,
        url=url,
        description=description,
        color=color if 0 <= color < 0x1000000 else DEFAULT_EMBED_COLOR,
    )

    if timestamp:
        if isinstance(timestamp, str):
            try:
                embed.timestamp = datetime.datetime.fromisoformat(
                    timestamp[:-1] if timestamp.endswith("Z") else timestamp
                )
            except ValueError:
                pass
        elif isinstance(timestamp, datetime.datetime):
            embed.timestamp = timestamp

    if author_name:
        embed.set_author(name=author_name, url=author_url, icon_url=author_icon_url)

    if thumbnail_url:
        embed.set_thumbnail(url=thumbnail_url)

    if image_url:
        embed.set_image(url=image_url)

    for field in fields:
        if isinstance(field, dict):
            embed.add_field(
                name=field.get("name", ""),
                value=field.get("value", ""),
                inline=field.get("inline", True),
            )
        else:
            embed.add_field(name=field[0], value=field[1], inline=field[2])

    if footer_text:
        embed.set_footer(text=footer_text, icon_url=footer_icon_url)

    return embed


async def send(
    channel: common.Channel,
    author_name: Optional[str] = EmptyEmbed,
    author_url: Optional[str] = EmptyEmbed,
    author_icon_url: Optional[str] = EmptyEmbed,
    title: Optional[str] = EmptyEmbed,
    url: Optional[str] = EmptyEmbed,
    thumbnail_url: Optional[str] = EmptyEmbed,
    description: Optional[str] = EmptyEmbed,
    image_url: Optional[str] = EmptyEmbed,
    color: int = DEFAULT_EMBED_COLOR,
    fields: Union[list, tuple] = (),
    footer_text: Optional[str] = EmptyEmbed,
    footer_icon_url: Optional[str] = EmptyEmbed,
    timestamp: Optional[str] = EmptyEmbed,
):
    """
    Sends an embed with a much more tight function. If the channel is
    None it will return the embed instead of sending it.
    """

    embed = create(
        author_name=author_name,
        author_url=author_url,
        author_icon_url=author_icon_url,
        title=title,
        url=url,
        thumbnail_url=thumbnail_url,
        description=description,
        image_url=image_url,
        color=color,
        fields=fields,
        footer_text=footer_text,
        footer_icon_url=footer_icon_url,
        timestamp=timestamp,
    )

    return await channel.send(embed=embed)


async def replace(
    message: discord.Message,
    author_name: Optional[str] = EmptyEmbed,
    author_url: Optional[str] = EmptyEmbed,
    author_icon_url: Optional[str] = EmptyEmbed,
    title: Optional[str] = EmptyEmbed,
    url: Optional[str] = EmptyEmbed,
    thumbnail_url: Optional[str] = EmptyEmbed,
    description: Optional[str] = EmptyEmbed,
    image_url: Optional[str] = EmptyEmbed,
    color: int = DEFAULT_EMBED_COLOR,
    fields: Union[list, tuple] = (),
    footer_text: Optional[str] = EmptyEmbed,
    footer_icon_url: Optional[str] = EmptyEmbed,
    timestamp: Optional[str] = EmptyEmbed,
):
    """
    Replaces the embed of a message with a much more tight function
    """
    embed = create(
        author_name=author_name,
        author_url=author_url,
        author_icon_url=author_icon_url,
        title=title,
        url=url,
        thumbnail_url=thumbnail_url,
        description=description,
        image_url=image_url,
        color=color,
        fields=fields,
        footer_text=footer_text,
        footer_icon_url=footer_icon_url,
        timestamp=timestamp,
    )
    return await message.edit(embed=embed)


class PagedEmbed:
    def __init__(
        self,
        message: discord.Message,
        pages: list[discord.Embed],
        caller: Optional[Union[discord.Member, Iterable[discord.Member]]] = None,
        command: Optional[str] = None,
        start_page: int = 0,
    ):
        """
        Create an embed which can be controlled by reactions. The footer of the
        embeds will be overwritten. If the optional "command" argument
        is set the embed page will be refreshable. The pages argument must
        have at least one embed.

        Args:
            message (discord.Message): The message to overwrite. For commands,
            it would be self.response_msg

            pages (list[discord.Embed]): The list of embeds to change
            pages between

            caller (Optional[discord.Member]): The user (or list of users) that can
            control the embed. Defaults to None (everyone can control it).

            command (Optional[str]): Optional argument to support kh!refresh.
            Defaults to None.

            start_page (int): The page to start from. Defaults to 0.
        """
        self.pages = pages
        self.current_page = start_page
        self.message = message
        self.parent_command = command
        self.is_on_info = False

        self.control_emojis = {
            "first": ("", ""),
            "prev": ("◀️", "Go to the previous page"),
            "stop": ("⏹️", "Deactivate the buttons"),
            "info": ("ℹ️", "Show this information page"),
            "next": ("▶️", "Go to the next page"),
            "last": ("", ""),
        }

        if len(self.pages) >= 3:
            self.control_emojis["first"] = ("⏪", "Go to the first page")
            self.control_emojis["last"] = ("⏩", "Go to the last page")

        self.killed = False

        if isinstance(caller, discord.Member):
            caller = (caller,)

        self.caller = caller

        self.help_text = ""
        for emoji, desc in self.control_emojis.values():
            if emoji:
                self.help_text += f"{emoji}: {desc}\n"

    async def add_control_emojis(self):
        """Add the control reactions to the message."""
        for emoji in self.control_emojis.values():
            if emoji[0]:
                await self.message.add_reaction(emoji[0])

    async def handle_reaction(self, reaction: str):
        """Handle a reaction."""
        if reaction == self.control_emojis.get("next", ("",))[0]:
            await self.set_page(self.current_page + 1)

        if reaction == self.control_emojis.get("prev", ("",))[0]:
            await self.set_page(self.current_page - 1)

        if reaction == self.control_emojis.get("first", ("",))[0]:
            await self.set_page(0)

        if reaction == self.control_emojis.get("last", ("",))[0]:
            await self.set_page(len(self.pages) - 1)

        if reaction == self.control_emojis.get("stop", ("",))[0]:
            self.killed = True

        if reaction == self.control_emojis.get("info", ("",))[0]:
            await self.show_info_page()

    async def show_info_page(self):
        """Create and show the info page."""
        self.is_on_info = not self.is_on_info
        if self.is_on_info:
            info_page_embed = create(
                description=self.help_text,
                footer_text=self.get_footer_text(self.current_page),
            )
            await self.message.edit(embed=info_page_embed)
        else:
            await self.message.edit(embed=self.pages[self.current_page])

    async def set_page(self, num: int):
        """Set the current page and display it."""
        self.is_on_info = False
        self.current_page = num % len(self.pages)
        await self.message.edit(embed=self.pages[self.current_page])

    async def _setup(self):
        if not self.pages:
            await replace(
                self.message,
                title="Internal error occured!",
                description="Got empty embed list for PagedEmbed",
                color=0xFF0000,
            )
            return False

        if len(self.pages) == 1:
            await self.message.edit(embed=self.pages[0])
            return False

        for i, page in enumerate(self.pages):
            footer = self.get_footer_text(i)

            page.set_footer(text=footer)

        await self.message.edit(embed=self.pages[self.current_page])
        await self.add_control_emojis()

        return True

    def get_footer_text(self, page_num: int):
        """Get the information footer text, which contains the current page."""
        footer = f"Page {page_num + 1} of {len(self.pages)}.\n"

        if self.parent_command:
            footer += "Refresh by replying to this message with `kh!refresh`\n"
            footer += f"Command: {self.parent_command}"

        return footer

    async def check(self, event):
        """Check if the event from `raw_reaction_add` can be passed down to `handle_rection`"""
        if event.message_id != self.message.id:
            return False

        if event.member is None:
            raise BotException(
                "Paged embeds are not supported in DMs.",
                "If you are seeing this in a public channel"
                ", please report this as a bug.",
            )

        if event.member.bot:
            return False

        await self.message.remove_reaction(str(event.emoji), event.member)
        if self.caller:
            for member in self.caller:
                if member.id == event.user_id:
                    return True

            for role in event.member.roles:
                if not False and role.id in common.ADMIN_ROLES:
                    return True

    async def mainloop(self):
        """Start the mainloop. This checks for reactions and handles them."""
        if not await self._setup():
            return

        while not self.killed:
            try:
                event = await common.bot.wait_for("raw_reaction_add", timeout=60)

                if await self.check(event):
                    await self.handle_reaction(str(event.emoji))

            except asyncio.TimeoutError:
                self.killed = True

        await self.message.clear_reactions()


def get_doc_from_func(func: typing.Callable):
    """
    Get the type, signature, description and other information from docstrings.

    Args:
        func (typing.Callable): The function to get formatted docs for

    Returns:
        Dict[str] or Dict[]: The type, signature and description of
        the string. An empty dict will be returned if the string begins
        with "->skip" or there was no information found
    """
    string = func.__doc__
    if not string:
        return {}

    string = string.strip()
    if string.startswith("->skip"):
        return {}

    finds = regex.findall(string.split("-----")[0])
    current_key = ""
    data = {}
    if finds:
        for find in finds:
            if find[0].startswith("->"):
                current_key = find[0][2:].strip()
                continue

            if not current_key:
                continue

            # remove useless whitespace
            value = re.sub("  +", "", find[1].strip())
            data[current_key] = value
            current_key = ""

    return data


async def send_help_message(
    original_msg: discord.Message,
    invoker: discord.Member,
    commands: tuple[str, ...],
    cmds_and_funcs: dict[str, typing.Callable],
    groups: dict[str, list],
    page: int = 0,
):
    """
    Edit original_msg to a help message. If command is supplied it will
    only show information about that specific command. Otherwise sends
    the general help embed.

    Args:
        original_msg: The message to edit
        invoker: The member who requested the help command
        commands: A tuple of command names passed by user for help.
        cmds_and_funcs: The name-function pairs to get the docstrings from
        groups: The name-list pairs of group commands
        page: The page of the embed, 0 by default
    """

    doc_fields = {}
    embeds = []

    if not commands:
        functions = {}
        for key, func in cmds_and_funcs.items():
            if hasattr(func, "groupname"):
                key = f"{func.groupname} {' '.join(func.subcmds)}"
            functions[key] = func

        for func in functions.values():
            data = get_doc_from_func(func)
            if not data:
                continue

            if not doc_fields.get(data["type"]):
                doc_fields[data["type"]] = ["", "", True]

            doc_fields[data["type"]][0] += f"{data['signature'][2:]}\n"
            doc_fields[data["type"]][1] += (
                f"`{data['signature']}`\n" f"{data['description']}\n\n"
            )

        doc_fields_cpy = doc_fields.copy()

        for doc_field_name in doc_fields:
            doc_field_list = doc_fields[doc_field_name]
            doc_field_list[1] = f"```\n{doc_field_list[0]}\n```\n\n{doc_field_list[1]}"
            doc_field_list[0] = f"__**{doc_field_name}**__"

        doc_fields = doc_fields_cpy

        embeds.append(
            discord.Embed(
                title=common.BOT_HELP_PROMPT["title"],
                description=common.BOT_HELP_PROMPT["description"],
                color=common.BOT_HELP_PROMPT["color"],
            )
        )
        for doc_field in list(doc_fields.values()):
            body = f"{doc_field[0]}\n\n{doc_field[1]}"
            embeds.append(
                create(
                    title=common.BOT_HELP_PROMPT["title"],
                    description=body,
                    color=common.BOT_HELP_PROMPT["color"],
                )
            )

    elif commands[0] in cmds_and_funcs:
        func_name = commands[0]
        funcs = groups[func_name] if func_name in groups else []
        funcs.insert(0, cmds_and_funcs[func_name])

        for func in funcs:
            if (
                commands[1:]
                and commands[1:] != getattr(func, "subcmds", ())[: len(commands[1:])]
            ):
                continue

            doc = get_doc_from_func(func)
            if not doc:
                # function found, but does not have help.
                return await replace(
                    original_msg,
                    title="Could not get docs",
                    description="Command has no documentation",
                    color=0xFF0000,
                )

            body = f"`{doc['signature']}`\n`Category: {doc['type']}`\n\n"

            desc = doc["description"]

            ext_desc = doc.get("extended description")
            if ext_desc:
                desc = f"> *{desc}*\n\n{ext_desc}"

            desc_list = desc.split(sep="+===+")

            body += f"**Description:**\n{desc_list[0]}"

            embed_fields = []

            example_cmd = doc.get("example command")
            if example_cmd:
                embed_fields.append(["Example command(s):", example_cmd, True])

            if len(desc_list) == 1:
                embeds.append(
                    create(
                        title=f"Help for `{func_name}`",
                        description=body,
                        color=common.BOT_HELP_PROMPT["color"],
                        fields=embed_fields,
                    )
                )
            else:
                embeds.append(
                    create(
                        title=f"Help for `{func_name}`",
                        description=body,
                        color=common.BOT_HELP_PROMPT["color"],
                    )
                )
                desc_list_len = len(desc_list)
                for i in range(1, desc_list_len):
                    embeds.append(
                        create(
                            title=f"Help for `{func_name}`",
                            description=desc_list[i],
                            color=common.BOT_HELP_PROMPT["color"],
                            fields=embed_fields if i == desc_list_len - 1 else (),
                        )
                    )

    if not embeds:
        return await replace(
            original_msg,
            title="Command not found",
            description="No such command exists",
            color=0xFF0000,
        )

    await PagedEmbed(
        original_msg, embeds, invoker, f"help {' '.join(commands)}", page
    ).mainloop()
