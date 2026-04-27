import discord
import google.generativeai as genai
import os

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
CHANNEL_ID = int(os.environ.get("CHANNEL_ID"))

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    system_instruction="you are a chill funny discord bot. talk casually like a gen z person, lowercase only, short responses, like texting a friend. don't be cringe or try too hard."
)

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

chat_histories = {}

@client.event
async def on_ready():
    print(f"online as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.channel.id != CHANNEL_ID:
        return

    async with message.channel.typing():
        try:
            if CHANNEL_ID not in chat_histories:
                chat_histories[CHANNEL_ID] = model.start_chat(history=[])
            chat = chat_histories[CHANNEL_ID]
            response = chat.send_message(f"{message.author.display_name}: {message.content}")
            await message.channel.send(response.text)
        except Exception as e:
            await message.channel.send("ugh something broke lol try again")
            print(f"error: {e}")

client.run(DISCORD_TOKEN)
