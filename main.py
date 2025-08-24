import discord
from discord.ext import commands
import os
import requests
import yt_dlp as youtube_dl
from dotenv import load_dotenv
import re

load_dotenv()

TOKEN = os.getenv("TOKEN")
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

pattern = re.compile(r'([\s\.]+|^)john(\s+|$)', re.IGNORECASE | re.MULTILINE)


# ------------------ EVENTS ------------------ #
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if re.search(pattern, message.content):
        await message.channel.send("Did someone call me?")

    await bot.process_commands(message)


# ------------------ TEXT COMMANDS ------------------ #
@bot.command()
async def hello(ctx):
    await ctx.send("Hello!")


@bot.command()
async def joke(ctx):
    url = "https://icanhazdadjoke.com/"
    headers = {"Accept": "application/json"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        await ctx.send(response.json().get("joke"))
    else:
        await ctx.send("Sorry, I couldn't fetch a joke at this time.")


@bot.command()
async def help(ctx):
    help_message = (
        "Here are the commands you can use:\n"
        "!hello - Greet the bot\n"
        "!joke - Get a random joke\n"
        "!weird - Get a weird emoji\n"
        "!wrong - Get a wrong emoji\n"
        "!join - Bot joins your voice channel\n"
        "!leave - Bot leaves the voice channel\n"
        "!play <YouTube URL> - Play a YouTube video in voice channel"
    )
    await ctx.send(help_message)


@bot.command()
async def weird(ctx):
    await ctx.send('<:weird:1409203822064042058>')


@bot.command()
async def wrong(ctx):
    await ctx.send('<:wrong:1409209810062282782>')


# ------------------ VOICE COMMANDS ------------------ #
@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
    else:
        await ctx.send("You need to be in a voice channel first.")


@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
    else:
        await ctx.send("I am not connected to a voice channel.")


@bot.command()
async def play(ctx, url: str):
    if not ctx.voice_client:
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await channel.connect()
        else:
            await ctx.send("You need to be in a voice channel first.")
            return

    YDL_OPTIONS = {'format': 'bestaudio'}
    FFMPEG_OPTIONS = {'options': '-vn'}

    try:
        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info['url']

        vc = ctx.voice_client
        if vc.is_playing():
            vc.stop()
        vc.play(discord.FFmpegPCMAudio(audio_url, **FFMPEG_OPTIONS))

        await ctx.send(f" Now playing: {info['title']}")
    except Exception as e:
        await ctx.send(f" Error playing video: {e}")


# ------------------ RUN BOT ------------------ #
if not TOKEN:
    raise ValueError("No TOKEN found in .env file!")

bot.run(TOKEN)
