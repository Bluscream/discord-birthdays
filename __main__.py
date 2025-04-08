import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

class BirthdayBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix='!',
            intents=discord.Intents.default(),
            case_insensitive=True
        )
        self.birthday_data = {}
    
    async def setup_hook(self):
        """Setup hook called after login"""
        print(f"{self.user} has connected to Discord!")
        await self.load_extension("tasks")
    
    async def on_ready(self):
        """Event that triggers when the bot is ready"""
        print(f"{self.user} has connected to Discord!")
        await self.setup_hook()

def main():
    bot = BirthdayBot()
    TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"Failed to start bot: {str(e)}")

if __name__ == "__main__":
    main()