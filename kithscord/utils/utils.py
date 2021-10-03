"""
This file is a part of the source code for the KithscordBot.
This project has been licensed under the MIT license.
Copyright (c) 2021-present Kithare Organization

This file defines some important utility functions.
"""

from __future__ import annotations
import asyncio

import io
import platform
import stat
import subprocess
import zipfile
from pathlib import Path
from typing import Optional

import aiohttp
import discord

from kithscord.commands.parser import BotException
from kithscord.utils import embed_utils

KCR = "kcr.exe" if platform.system() == "Windows" else "kcr"

dist = Path("dist") / "Kithare" / KCR
is_pulling = False


def quotify(text: str, limit: int = 1024):
    """
    Format text in a discord quote, with newline handling
    """
    converted = text.strip().replace("\n", "\n> ")
    ret = f"> {converted}"
    if len(ret) > limit:
        ret = ret[: limit - 3] + "..."
    return ret


def rmtree(top: Path):
    """
    Reimplementation of shutil.rmtree, used to remove a directory. Returns a
    boolean on whether top was a directory or not (in the latter case this
    function does nothing).
    The reason shutil.rmtree itself is not used, is of a permission error on
    Windows.
    """
    if not top.is_dir():
        return False

    for newpath in top.iterdir():
        if not rmtree(newpath):
            # could not rmtree newpath because it is a file, hence unlink
            newpath.chmod(stat.S_IWUSR)
            newpath.unlink()

    top.rmdir()
    return True


def get_machine(is_32_bit: bool = False):
    """
    Utility to get string representation of the machine name. Possible return
    values:
    name    | Description           | Aliases
    ----------------------------------------
    x86     | Intel/AMD 32-bit      | i386, i686
    x64     | Intel/AMD 64-bit      | x86_64, amd64
    arm     | ARM 32-bit (very old) | armel, armv5 (or older)
    armv6   | ARM 32-bit (old)      | armhf, armv6l, armv6h
    armv7   | ARM 32-bit            | armhf, armv7l, armv7h
    arm64   | ARM 64-bit            | aarch64, armv8l, armv8 (or newer)
    ppc64le | PowerPC achitecture   | ppc64el (debian terminology)
    s390x   | IBM (big endian)      | None
    Unknown | Architecture could not be determined
    The function can also return other values platform.machine returns, without
    any modifications
    """
    machine = platform.machine()
    machine_lowered = machine.lower()
    if machine.endswith("86"):
        return "x86"

    if machine_lowered in {"x86_64", "amd64", "x64"}:
        return "x86" if is_32_bit else "x64"

    if machine_lowered in {"armv8", "armv8l", "arm64", "aarch64"}:
        return "armv7" if is_32_bit else "arm64"

    if machine_lowered.startswith("arm"):
        if "v7" in machine_lowered or "hf" in machine_lowered:
            return "armv7"

        if "v6" in machine_lowered:
            return "armv6"

        return "arm"

    if machine == "ppc64el":
        return "ppc64le"

    if not machine:
        return "Unknown"

    return machine


async def pull_kithare(
    response: Optional[discord.Message] = None, branch: str = "main"
):
    """
    Pull and install Kithare from github actions installers
    """
    global is_pulling

    temp = Path("tempdir")
    if is_pulling:
        raise BotException(
            "Pull failed!",
            "You cannot pull while another pull operation is running",
        )

    is_pulling = True
    try:
        if response is not None:
            await embed_utils.replace(
                response,
                title="Pulling Kithare",
                description="Please wait while Kithare is being installed",
                thumbnail_url="https://i.giphy.com/media/Ju7l5y9osyymQ/200.gif",
            )

        rmtree(dist.parents[1])

        machine = get_machine()
        system = platform.system().lower()
        if system == "linux" and machine not in {"x86", "x64"}:
            system += "-multiarch"

        link = "https://nightly.link/Kithare/Kithare/workflows/"
        link += f"{system}/{branch}/kithare-{system}-installers.zip"

        async with aiohttp.ClientSession() as session:
            async with session.get(link) as linkobj:
                if linkobj.content_type != "application/zip":
                    raise BotException(
                        "Could not install Kithare!",
                        "Make sure the branch exists, and github actions ran on it",
                    )

                with zipfile.ZipFile(io.BytesIO(await linkobj.read()), "r") as zipped:
                    zipped.extractall(temp)

        try:
            # get first installer that matches
            installzip = list(temp.glob(f"*{machine}.zip"))[0]
        except IndexError:
            raise BotException(
                "Could not install Kithare!",
                "Could not find installable zip package for the bot host machine",
            ) from None

        with zipfile.ZipFile(installzip, "r") as zipped:
            zipped.extractall(dist.parents[1])

        # fix permissions on the dist dir, because ZipFile messes them up
        for file in dist.parents[1].rglob("*"):
            file.chmod(0o775)

        if response is not None:
            await embed_utils.replace(
                response,
                title="Pulling Kithare",
                description="Kithare installation succeeded",
                color=0x00FF00,
            )

    finally:
        rmtree(temp)
        is_pulling = False


async def setup_kcr():
    """
    Pulls Kithare if it is not installed yet
    """
    if not dist.is_file() and not is_pulling:
        await pull_kithare()


async def run_kcr(*args: str, timeout: int = 5, recurse: bool = True):
    """
    Run kcr command
    """
    while is_pulling:
        await asyncio.sleep(0.1)

    try:
        return subprocess.run(
            (dist, *args),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            text=True,
        ).stdout

    except FileNotFoundError:
        if not recurse:
            raise BotException(
                "Could not execute Kithare command!",
                "Kithare has not been configured correctly on the bot runner!\n"
                "Automatic recovery has failed!\n"
                "PS: Bot Admin, this is likely a bug in the bot itself, fix it",
            ) from None

        await pull_kithare()
        return await run_kcr(*args, timeout=timeout, recurse=False)


def format_discord_link(link: str, guild_id: int):
    """
    Format a discord link to a channel or message
    """
    link = link.lstrip("<").rstrip(">").rstrip("/")

    for prefix in (
        f"https://discord.com/channels/{guild_id}/",
        f"https://www.discord.com/channels/{guild_id}/",
    ):
        if link.startswith(prefix):
            link = link[len(prefix) :]

    return link


def format_time(
    seconds: float,
    decimal_places: int = 4,
    unit_data: tuple[tuple[float, str], ...] = (
        (1.0, "s"),
        (1e-03, "ms"),
        (1e-06, "\u03bcs"),
        (1e-09, "ns"),
        (1e-12, "ps"),
        (1e-15, "fs"),
        (1e-18, "as"),
        (1e-21, "zs"),
        (1e-24, "ys"),
    ),
):
    """
    Formats time with a prefix
    """
    for fractions, unit in unit_data:
        if seconds >= fractions:
            return f"{seconds / fractions:.0{decimal_places}f} {unit}"
    return "very fast"


def format_byte(size: int, decimal_places: int = 3):
    """
    Formats a given size and outputs a string equivalent to B, KB, MB, or GB
    """
    if size < 1e03:
        return f"{round(size, decimal_places)} B"
    if size < 1e06:
        return f"{round(size / 1e3, decimal_places)} KB"
    if size < 1e09:
        return f"{round(size / 1e6, decimal_places)} MB"

    return f"{round(size / 1e9, decimal_places)} GB"


def split_long_message(message: str, limit: int = 2000):
    """
    Splits message string by 2000 characters with safe newline splitting
    """
    split_output: list[str] = []
    lines = message.split("\n")
    temp = ""

    for line in lines:
        if len(temp) + len(line) + 1 > limit:
            split_output.append(temp[:-1])
            temp = line + "\n"
        else:
            temp += line + "\n"

    if temp:
        split_output.append(temp)

    return split_output


def filter_id(mention: str):
    """
    Filters mention to get ID "<@!6969>" to "6969"
    Note that this function can error with ValueError on the int call, so the
    caller of this function must take care of that.
    """
    for char in ("<", ">", "@", "&", "#", "!", " "):
        mention = mention.replace(char, "")

    return int(mention)


def code_block(string: str, max_characters: int = 2000, code_type: str = ""):
    """
    Formats text into discord code blocks
    """
    string = string.replace("```", "\u200b`\u200b`\u200b`\u200b")
    len_ticks = 7 + len(code_type)

    if len(string) > max_characters - len_ticks:
        return f"```{code_type}\n{string[:max_characters - len_ticks - 4]} ...```"
    else:
        return f"```{code_type}\n{string}```"
