import discord
from discord.ext import commands, tasks
from datetime import date, datetime
import json
import os

class BirthdayBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix='!',
            intents=discord.Intents.default(),
            case_insensitive=True
        )
        self.birthday_data = {}

def create_bot():
    bot = BirthdayBot()
    
    @bot.event
    async def on_ready():
        print(f"{bot.user} has connected to Discord!")
        
        # Load existing birthday data
        if os.path.exists("birthdays.json"):
            global birthday_data
            with open("birthdays.json", "r") as f:
                bot.birthday_data = json.load(f)
        
        # Start the birthday checker task
        bot.check_birthdays.start()

    @tasks.loop(hours=24)
    async def check_birthdays():
        today = date.today()
        
        for guild_id, guild_data in bot.birthday_data.items():
            guild = bot.get_guild(int(guild_id))
            
            if not guild:
                continue
                
            for member_id, birthday in guild_data["members"].items():
                member_birthday = date.fromisoformat(birthday["date"])
                
                if today.month == member_birthday.month and \
                   today.day == member_birthday.day:
                    await create_birthday_event(guild, member_birthday)

    async def create_birthday_event(guild, birthday):
        event_name = f"{guild.name}'s Birthday Celebration"
        description = f"It's someone's birthday in {guild.name}!"
        
        try:
            event = await guild.create_scheduled_event(
                name=event_name,
                description=description,
                start_time=datetime.now(),
                end_time=datetime.now(),
                privacy_level=discord.EventPrivacyLevel.GUILD_ONLY
            )
            
            # Send announcement
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).send_messages:
                    await channel.send(
                        f"🎉 Someone in {guild.name} has a birthday today! "
                        f"Check out the new event created above to join in the celebration!"
                    )
                    break
                    
        except discord.Forbidden:
            print(f"Missing permissions to create events in {guild.name}")
        except discord.HTTPException as e:
            print(f"Error creating event in {guild.name}: {str(e)}")

    @bot.command(name="setbirthday", help="Set your birthday")
    async def set_birthday(ctx, month: int, day: int):
        if not (1 <= month <= 12 and 1 <= day <= 31):
            await ctx.send("Invalid date! Please use MM DD format.")
            return
            
        try:
            # Validate date exists
            date(2024, month, day)
            
            guild_id = str(ctx.guild.id)
            member_id = str(ctx.author.id)
            
            if guild_id not in bot.birthday_data:
                bot.birthday_data[guild_id] = {"members": {}}
                
            bot.birthday_data[guild_id]["members"][member_id] = {
                "date": f"{month:02d}-{day:02d}",
                "username": ctx.author.name,
                "discriminator": ctx.author.discriminator
            }
            
            # Save data
            with open("birthdays.json", "w") as f:
                json.dump(bot.birthday_data, f)
                
            await ctx.send(f"🎂 Your birthday has been set to {month}/{day}")
            
        except ValueError:
            await ctx.send("Invalid date! Please check the month and day.")

    @bot.command(name="listbirthdays", help="List upcoming birthdays")
    async def list_birthdays(ctx):
        guild_id = str(ctx.guild.id)
        
        if guild_id not in bot.birthday_data:
            await ctx.send("No birthdays recorded yet!")
            return
            
        today = date.today()
        upcoming_birthdays = []
        
        for member_id, birthday_data in bot.birthday_data[guild_id]["members"].items():
            bday_date = date.fromisoformat(birthday_data["date"])
            
            # Calculate days until birthday
            next_birthday = date(today.year, bday_date.month, bday_date.day)
            if next_birthday < today:
                next_birthday = date(today.year + 1, bday_date.month, bday_date.day)
                
            days_until = (next_birthday - today).days
            
            username = f"{birthday_data['username']}#{birthday_data['discriminator']}"
            upcoming_birthdays.append(f"{username}: {days_until} days until birthday")
            
        if not upcoming_birthdays:
            await ctx.send("No upcoming birthdays!")
        else:
            await ctx.send("\n".join(upcoming_birthdays))

    return bot

# Create and run the bot
bot = create_bot()

# Load token from environment variable
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

try:
    bot.run(TOKEN)
except Exception as e:
    print(f"Failed to start bot: {str(e)}")