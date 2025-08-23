import discord
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('john'):
        await message.channel.send('Did someone call me?')

    if message.content.startswith('!hello'):
        await message.channel.send('Hello!')

    if message.content.startswith('!joke'):
        joke = get_joke()
        await message.channel.send(joke)


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
