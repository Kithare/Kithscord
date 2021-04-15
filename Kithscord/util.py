import asyncio
from datetime import datetime
import discord

import common


async def log(msg: str):
    """
    Prints msg with the current time
    """
    now = datetime.now()
    print(f"[{now.strftime('%d/%m/%Y %H:%M:%S')}] {msg}")


async def construct_embed(
        title, description, color=0xAAFFFF,
        url_image=None, url_thumbnail=None, fields=[]):
    """
    Creates a discord.Embed with the provided arguments
    """
    embed = discord.Embed(title=title, description=description, color=color)

    if url_image:
        embed.set_image(url=url_image)
    if url_thumbnail:
        embed.set_thumbnail(url=url_thumbnail)
    for field in fields:
        embed.add_field(name=field[0], value=field[1], inline=field[2])

    return embed


async def edit_embed(
        message, title, description, color=0xAAFFFF,
        url_image=None, url_thumbnail=None, fields=[]
):
    """
    Edits the embed of a message with a much more tight function
    """
    return await message.edit(embed=await construct_embed(
        title, description, color,
        url_image, url_thumbnail, fields
    ))


async def send_embed(
        channel, title, description, color=0xAAFFFF,
        url_image=None, url_thumbnail=None, fields=[]
):
    """
    Sends an embed with a much more tight function
    """
    return await channel.send(embed=await construct_embed(
        title, description, color,
        url_image, url_thumbnail, fields
    ))


def code_block(string: str, max_characters=2048):
    string = string.replace("```", "\u200b`\u200b`\u200b`\u200b")
    max_characters -= 7

    if len(string) > max_characters:
        return f"```\n{string[:max_characters - 7]} ...```"
    else:
        return f"```\n{string[:max_characters]}```"


def discordify(message):
    """Converts normal string into "discord" string that includes backspaces to cancel out unwanted changes"""
    if '\\' in message:
        message = message.replace('\\', r'\\')
    if '*' in message:
        message = message.replace('*', r'\*')
    if '`' in message:
        message = message.replace('`', r'\`')
    if '_' in message:
        message = message.replace('_', r'\_')
    return message
