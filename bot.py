import openai
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

# Load environment variables
load_dotenv()

# Discord Bot Token
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# OpenAI API Key
openai.api_key = os.getenv("OPENAI_BOT_TOKEN")

# Setup the bot
intents = discord.Intents.default()
intents.message_content = True  # Allow reading message content

bot = commands.Bot(command_prefix="!", intents=intents)

# Dictionary to store conversation history per user
conversation_history = {}
MAX_HISTORY = 10

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

@bot.event
async def on_message(message):
    # Prevent the bot from responding to its own messages or other bots
    if message.author.bot:
        return

    # Check if the message starts with the command prefix to process commands
    if message.content.startswith(bot.command_prefix):
        await bot.process_commands(message)
        return

    user_id = message.author.id

    # Initialize conversation history for the user if not present
    if user_id not in conversation_history:
        conversation_history[user_id] = []

    # Append the user's message to their conversation history
    conversation_history[user_id].append({"role": "user", "content": message.content})

    # Limit the history to the last MAX_HISTORY messages to manage token usage
    if len(conversation_history[user_id]) > MAX_HISTORY:
        conversation_history[user_id] = conversation_history[user_id][-MAX_HISTORY:]

    try:
        # Generate a response using OpenAI's ChatCompletion API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # You can use "gpt-4" if available and needed
            messages=conversation_history[user_id],
            max_tokens=75,
            temperature=0.7,
            n=1,
            stop=None,
        )

        reply = response['choices'][0]['message']['content'].strip()

        # Append the assistant's reply to the conversation history
        conversation_history[user_id].append({"role": "assistant", "content": reply})

        # Send the reply back to the Discord channel
        await message.channel.send(reply)

    except openai.error.OpenAIError as e:
        print(f"OpenAI API error: {e}")
        await message.channel.send("Sorry, I'm having trouble processing your request right now.")
    except Exception as e:
        print(f"Unexpected error: {e}")
        await message.channel.send("An unexpected error occurred. Please try again later.")

# Run the bot
bot.run(DISCORD_BOT_TOKEN)
