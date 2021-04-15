import discord

from overload import *
import util


@export(0)
async def version(args, msg: discord.Message, response: discord.Message):
    await util.edit_embed(response, "Version", "Kithare Version: 0.0.0\nBot Version: 69.69")
