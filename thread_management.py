import discord
import json

JSON_FILE = "threads.json"

# Loads the data from the JSON file
def load_data():
    try:
        with open(JSON_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        # If the file doesn't exist, return an empty dictionary
        return {}
    except json.JSONDecodeError:
        # If the file is corrupted or empty, return an empty dictionary
        return {}

def save_data(data):
    """Save data to the JSON file."""
    with open(JSON_FILE, "w") as file:
        json.dump(data, file, indent=4)


# Function that creates a thread in the channel where the message was sent. 
# Arguments: message-the message that started the conversation; bot-the discord bot
async def create_thread(message, bot):
    user_id = message.author.id

    if hasattr(bot, 'active_threads') and user_id in bot.active_threads:
        existing_thread = bot.active_threads[user_id]
        await message.channel.send(f"{message.author.mention}, you already have an active thread: {existing_thread.mention}")
        return

    try:
        # Create a private thread from the message
        thread = await message.channel.create_thread(
            name=f"Chat with {message.author.display_name}",
            type=discord.ChannelType.private_thread,
            invitable=False,  # Set to True if you want others to join
            auto_archive_duration=60  # Duration in minutes
        )
        
        # Send a welcome message in the thread
        await thread.send(f"Hello {message.author.mention}! I'm here to assist you.")
        
        # Add the user to the thread
        await thread.add_user(message.author)
        
        # Add the bot to the thread (optional, as it has access by default)
        await thread.add_user(bot.user)
        
        print(f"Thread '{thread.name}' created for {message.author.display_name}")

        # Track the active thread
        if not hasattr(bot, 'active_threads'):
            bot.active_threads = {}
        bot.active_threads[user_id] = thread

        # Optionally, remove the thread from active_threads after it's archived
        async def remove_thread_after_archive():
            await thread.wait_until_archived()
            if hasattr(bot, 'active_threads') and user_id in bot.active_threads:
                del bot.active_threads[user_id]
                print(f"Thread '{thread.name}' archived and removed from active threads.")

        bot.loop.create_task(remove_thread_after_archive())

    except discord.errors.Forbidden:
        print("Bot lacks permissions to create threads in this channel.")
        await message.channel.send("I don't have permission to create threads here.")
    except Exception as e:
        print(f"Error creating thread: {e}")
        await message.channel.send("An error occurred while trying to create a thread.")
