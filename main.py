import discord
import os
from discord.ext import commands
import requests
import yt_dlp as youtube_dl
import asyncio
import json
import re
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

pattern = re.compile(r'([\s\.]+|^)john(\s+|$)', re.IGNORECASE | re.MULTILINE)


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
    else:
        await ctx.send("You are not connected to a voice channel.")


async def leave(ctx):
    if ctx.voice_client:
        await ctx.guild.voice_client.disconnect()
    else:
        await ctx.send("I am not connected to a voice channel.")


async def play(ctx, url: str):
    if not ctx.voice_client:
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await channel.connect()
        else:
            await ctx.send("You are not connected to a voice channel.")
            return

    YDL_OPTIONS = {'format': 'bestaudio'}
    FFMPEG_OPTIONS = {'options': '-vn'}

    with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=False)
        audio_url = info['url']

    vc = ctx.voice_client
    vc.stop()
    vc.play(discord.FFmpegPCMAudio(audio_url, **FFMPEG_OPTIONS))

    await ctx.send(f'Now playing: {info["title"]}')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if re.search(pattern, message.content):
        await message.channel.send("Did someone call me?")

    if message.content.startswith('!hello'):
        await message.channel.send('Hello!')

    if message.content.startswith('!joke'):
        joke = get_joke()
        await message.channel.send(joke)

    if message.content.startswith('!help'):
        help_message = (
            "Here are the commands you can use:\n"
            "!hello - Greet the bot\n"
            "!joke - Get a random joke\n"
            "!weird - Get a weird pic\n"
            "!wrong - Get a wrong pic\n"
            "!help - Show this help message"
        )
        await message.channel.send(help_message)

    if message.content.startswith('!weird'):
        await message.channel.send('<:weird:1409203822064042058>')

    if message.content.startswith('!wrong'):
        await message.channel.send('<:wrong:1409209810062282782>')


def get_joke():
    url = "https://icanhazdadjoke.com/"
    headers = {"Accept": "application/json"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("joke")
    else:
        return "Sorry, I couldn't fetch a joke at this time."


token = os.getenv('TOKEN')
print("Loaded token:", token)

client.run(token)
