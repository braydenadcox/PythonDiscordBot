import openai
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from thread_management import * # Import the create_thread function

# Load environment variables
load_dotenv()

# Discord Bot, OpenAI API, and Channel Activation Keys from .env file
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
ACTIVATING_CHANNEL_ID = int(os.getenv("BOT_ACTIVATION_CHANNEL_ID"))  # Ensure it's an integer
OPENAI_API_KEY = os.getenv("OPENAI_BOT_TOKEN")
openai.api_key = OPENAI_API_KEY

# Setup the bot
intents = discord.Intents.default()
intents.message_content = True  # Allow reading message content
intents.guilds = True
intents.members = True  # Needed for member-related events

bot = commands.Bot(command_prefix="!", intents=intents)

# Dictionary to store conversation history per thread
conversation_history = {}
MAX_HISTORY = 10

# Dictionary to track active threads per user (initialized in thread_management.py if needed)
bot.active_threads = {}

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

@bot.event
async def on_message(message):
    # Prevent the bot from responding to its own messages or other bots
    if message.author.bot:
        return

    # Check if the message is in the activating channel to create a thread
    if message.channel.id == ACTIVATING_CHANNEL_ID:
        await create_thread(message, bot)  # Pass the bot instance
        return  # Exit after creating a thread to prevent processing the message further

    # Check if the message is within a thread created by the bot
    if isinstance(message.channel, discord.Thread):
        await handle_thread_message(message)
        return

    # Process other commands if any
    await bot.process_commands(message)

async def handle_thread_message(message):
    """
    Handles messages sent within a thread by interacting with OpenAI's API.
    
    Args:
        message (discord.Message): The message sent in the thread.
    """
    thread_id = message.channel.id  # Using thread ID to manage conversation history

    # Initialize conversation history for the thread if not present
    if thread_id not in conversation_history:
        conversation_history[thread_id] = []

    # Append the user's message to the conversation history
    conversation_history[thread_id].append({"role": "user", "content": message.content})

    # Limit the history to the last MAX_HISTORY * 2 messages to account for user and assistant messages
    if len(conversation_history[thread_id]) > MAX_HISTORY * 2:
        conversation_history[thread_id] = conversation_history[thread_id][-MAX_HISTORY * 2:]

    # Generates a response using OpenAI's ChatCompletion API - This is what makes the model have human responses with the database plus the model of response
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  
            messages=conversation_history[thread_id],
            max_tokens=150,
            temperature=0.7,
            n=1,
            stop=None,
        )

        reply = response['choices'][0]['message']['content'].strip()

        conversation_history[thread_id].append({"role": "assistant", "content": reply})

        await message.channel.send(reply)

    except openai.error.OpenAIError as e:
        print(f"OpenAI API error: {e}")
        await message.channel.send("Sorry, I'm having trouble processing your request right now.")
    except Exception as e:
        print(f"Unexpected error: {e}")
        await message.channel.send("An unexpected error occurred. Please try again later.")

bot.run(DISCORD_BOT_TOKEN)
