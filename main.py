import discord
from discord.ext import commands
import yt_dlp as youtube_dl
from asyncio import Queue
import os
import requests
import re
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# ------------------ GLOBALS ------------------ #
queues = {}  # server_id -> Queue
current_song = {}  # server_id -> currently playing

YDL_OPTIONS = {'format': 'bestaudio'}
FFMPEG_PATH = r"C:\ffmpeg\bin\ffmpeg.exe"  # Use full path if PATH not set
FFMPEG_OPTIONS = {'executable': FFMPEG_PATH, 'options': '-vn'}

# Regex for "john"
pattern = re.compile(r'([\s\.]+|^)john(\s+|$)', re.IGNORECASE | re.MULTILINE)

# ------------------ HELPER FUNCTIONS ------------------ #


async def play_next(ctx):
    server_id = ctx.guild.id
    if queues[server_id].empty():
        await ctx.voice_client.disconnect()
        return

    url = await queues[server_id].get()
    with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=False)
        audio_url = info['url']

    def after_playing(error):
        bot.loop.create_task(play_next(ctx))

    vc = ctx.voice_client
    vc.play(discord.FFmpegPCMAudio(audio_url, **
            FFMPEG_OPTIONS), after=after_playing)
    current_song[server_id] = info['title']
    bot.loop.create_task(ctx.send(f"🎶 Now playing: {info['title']}"))


def get_joke():
    url = "https://icanhazdadjoke.com/"
    headers = {"Accept": "application/json"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("joke")
    else:
        return "Sorry, I couldn't fetch a joke at this time."

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

    await bot.process_commands(message)  # process other commands

# ------------------ TEXT COMMANDS ------------------ #


@bot.command()
async def hello(ctx):
    await ctx.send("Hello! 😀")


@bot.command()
async def joke(ctx):
    await ctx.send(get_joke())


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
        "!play <YouTube URL> - Play a YouTube video in voice channel\n"
        "!pause - Pause the music\n"
        "!resume - Resume paused music\n"
        "!skip - Skip current song\n"
        "!queue_list - Show the song queue"
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
        await ctx.send(f"Joined {channel.name}!")
    else:
        await ctx.send("You need to be in a voice channel first.")


@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Disconnected from voice channel.")
    else:
        await ctx.send("I am not connected to a voice channel.")


@bot.command()
async def play(ctx, url: str):
    """Play or queue a YouTube video"""
    server_id = ctx.guild.id

    if not ctx.voice_client:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.send("You need to be in a voice channel first.")
            return

    if server_id not in queues:
        queues[server_id] = Queue()

    await queues[server_id].put(url)
    await ctx.send(f"✅ Added to queue: {url}")

    vc = ctx.voice_client
    if not vc.is_playing() and queues[server_id].qsize() == 1:
        await play_next(ctx)


@bot.command()
async def pause(ctx):
    vc = ctx.voice_client
    if vc and vc.is_playing():
        vc.pause()
        await ctx.send("⏸ Paused the music.")
    else:
        await ctx.send("No music is playing.")


@bot.command()
async def resume(ctx):
    vc = ctx.voice_client
    if vc and vc.is_paused():
        vc.resume()
        await ctx.send("▶ Resumed the music.")
    else:
        await ctx.send("No music is paused.")


@bot.command()
async def skip(ctx):
    vc = ctx.voice_client
    if vc and vc.is_playing():
        vc.stop()
        await ctx.send("⏭ Skipped the current song.")
    else:
        await ctx.send("No music is playing.")


@bot.command()
async def queue_list(ctx):
    server_id = ctx.guild.id
    if server_id in queues and not queues[server_id].empty():
        items = list(queues[server_id]._queue)
        message = "\n".join([f"{i+1}. {url}" for i, url in enumerate(items)])
        await ctx.send(f"🎵 Current queue:\n{message}")
    else:
        await ctx.send("Queue is empty.")

# ------------------ RUN BOT ------------------ #
if not TOKEN:
    raise ValueError("No TOKEN found in .env file!")

bot.run(TOKEN)
