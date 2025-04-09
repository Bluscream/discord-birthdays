import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

from strings import Strings
lang = Strings('de')

class BirthdayBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix='!',
            intents=discord.Intents.all(),
            case_insensitive=True
        )
        self.birthday_data = {}
        self.extensions_loaded = False  # Track extension loading status
        # self.tree = commands.CommandTree(self)
    
    async def on_ready(self):
        print(lang.get("bot.ready").format(self_user=self.user))
        if self.extensions_loaded: return
        self.extensions_loaded = True
        await self.load_extension("tasks")
        # await self.tree.sync()
        # print("Commands synced successfully!")

def main():
    bot = BirthdayBot()
    TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    try:
        bot.run(TOKEN)
    except Exception as err:
        print(lang.get('bot.failed').format(err=err))

if __name__ == "__main__":
    main()