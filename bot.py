import discord
from google import genai
from google.genai import types
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

print(f"token loaded: {bool(DISCORD_TOKEN)}")
print(f"gemini key loaded: {bool(GEMINI_API_KEY)}")

client_ai = genai.Client(api_key=GEMINI_API_KEY)

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
client = discord.Client(intents=intents)

chat_histories = {}

class PingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"alive")
    def log_message(self, format, *args):
        pass

def run_server():
    server = HTTPServer(("0.0.0.0", 8080), PingHandler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

@client.event
async def on_ready():
    print(f"online as {client.user}")
    print(f"in {len(client.guilds)} servers")

@client.event
async def on_message(message):
    print(f"message received from {message.author}: {message.content[:50]}")
    if message.author == client.user:
        return
    if client.user not in message.mentions:
        print("not mentioned, ignoring")
        return

    print("bot was mentioned, calling gemini...")
    async with message.channel.typing():
        try:
            channel_id = message.channel.id
            if channel_id not in chat_histories:
                chat_histories[channel_id] = []

            chat_histories[channel_id].append(
                types.Content(role="user", parts=[types.Part(text=f"{message.author.display_name}: {message.content}")])
            )

            response = client_ai.models.generate_content(
                model="gemini-2.0-flash",
                contents=chat_histories[channel_id],
                config=types.GenerateContentConfig(
                    system_instruction="you are a chill funny discord bot. talk casually like a gen z person, lowercase only, short responses, like texting a friend. don't be cringe or try too hard."
                )
            )

            reply = response.text
            chat_histories[channel_id].append(
                types.Content(role="model", parts=[types.Part(text=reply)))
            )

            await message.channel.send(reply)
        except Exception as e:
            await message.channel.send("ugh something broke lol try again")
            print(f"error: {e}")

client.run(DISCORD_TOKEN)
