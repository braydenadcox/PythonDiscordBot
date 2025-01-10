import discord
import random
import requests
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

def fetch_problems_by_difficulty(difficulty):
    """
    This function is the function that actually grabs the leetcode problems from the website. The function uses 
    GraphQL, a query that holds every single LeetCode problem and obtains one when called.
    """
    url = "https://leetcode.com/graphql"
    query = """
    query {
        problemsetQuestionListV2(
            limit: 3416
        ) {
            questions {
                title
                titleSlug
            }
        }
    }
    """
    response = requests.post(url, json={"query": query})

    print("API Response:", response.text)  # Debugging line

    if response.status_code == 200:
        data = response.json()
        questions = data["data"]["problemsetQuestionListV2"]["questions"]
        return [
            {"title": q["title"], "url": f"https://leetcode.com/problems/{q['titleSlug']}/"}
            for q in questions
        ]
    else:
        return None

    
    # Create intents
intents = discord.Intents.default()
intents.messages = True  # Allow bot to read messages in channels
intents.message_content = True # Manually enables message content intent
intents.guilds = True    # Allow bot to interact with server-related events

# Discord bot setup
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")


@bot.command()
async def leetcode(ctx, difficulty: str):
    problems = fetch_problems_by_difficulty(difficulty)
    if problems:
        problem = random.choice(problems)
        await ctx.send(f"Try this problem: **{problem['title']}**\n{problem['url']}")
    else:
        await ctx.send("Could not fetch problems. Please try again later.")

# Run the bot
if BOT_TOKEN:
    bot.run(BOT_TOKEN)
else:
    print("Unable to detect a bot token.")
