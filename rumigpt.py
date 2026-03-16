import discord
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

def ask_openrouter(prompt):
    """Send prompt to OpenRouter API and return assistant response"""
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek/deepseek-r1:free",  # ✅ free model
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ]
            },
            timeout=30
        )
        data = response.json()
        print("OpenRouter response:", data)

        # ✅ Check for API-level error
        if "error" in data:
            print("API Error:", data["error"])
            return f"API Error: {data['error'].get('message', 'Unknown error')}"

        # ✅ Safe check for 'choices'
        if "choices" not in data or len(data["choices"]) == 0:
            return "Sorry, I could not get a response from OpenRouter."

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        print("Error calling OpenRouter:", e)
        return "Sorry, something went wrong while contacting OpenRouter."

@client.event
async def on_ready():
    print(f"Bot is online as {client.user}")

@client.event
async def on_message(message):
    # Ignore bot's own messages
    if message.author == client.user:
        return

    # ✅ Only one trigger at a time — no double response
    if message.content.startswith("!ask"):
        prompt = message.content.replace("!ask", "", 1).strip()
    elif client.user.mentioned_in(message):
        prompt = message.content.replace(f"<@{client.user.id}>", "", 1).strip()
    else:
        return  # Ignore all other messages

    if not prompt:
        await message.channel.send("Please ask me something! Usage: `!ask your question`")
        return

    async with message.channel.typing():
        reply = ask_openrouter(prompt)

        # Split reply if too long for Discord (2000 char limit)
        if len(reply) > 2000:
            chunks = [reply[i:i+1997] for i in range(0, len(reply), 1997)]
            for chunk in chunks:
                await message.channel.send(chunk)
        else:
            await message.channel.send(reply)

# Run the bot
client.run(DISCORD_TOKEN)