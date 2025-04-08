# tasks.py
import discord
from discord.ext import commands, tasks
from datetime import date, datetime
import json
import os

class BirthdayTasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.birthday_data = {}
    
    @tasks.loop(hours=24)
    async def check_birthdays(self):
        """Check for birthdays every 24 hours"""
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            today = date.today()
            for guild_id, guild_data in self.birthday_data.items():
                guild = self.bot.get_guild(int(guild_id))
                if not guild:
                    continue
                
                for member_id, birthday in guild_data["members"].items():
                    member_birthday = date.fromisoformat(birthday["date"])
                    
                    if today.month == member_birthday.month and \
                       today.day == member_birthday.day:
                        await self.create_birthday_event(guild, member_birthday)
            
            await asyncio.sleep(86400)  # 24 hours

    async def create_birthday_event(self, guild, birthday):
        """Create a birthday event for the specified guild"""
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

    @commands.command(name="setbirthday", help="Set your birthday")
    async def set_birthday(self, ctx, month: int, day: int):
        if not (1 <= month <= 12 and 1 <= day <= 31):
            await ctx.send("Invalid date! Please use MM DD format.")
            return
            
        try:
            # Validate date exists
            date(2024, month, day)
            
            guild_id = str(ctx.guild.id)
            member_id = str(ctx.author.id)
            
            if guild_id not in self.birthday_data:
                self.birthday_data[guild_id] = {"members": {}}
                
            self.birthday_data[guild_id]["members"][member_id] = {
                "date": f"{month:02d}-{day:02d}",
                "username": ctx.author.name,
                "discriminator": ctx.author.discriminator
            }
            
            # Save data
            with open("birthdays.json", "w") as f:
                json.dump(self.birthday_data, f)
                
            await ctx.send(f"🎂 Your birthday has been set to {month}/{day}")
            
        except ValueError:
            await ctx.send("Invalid date! Please check the month and day.")

    @commands.command(name="listbirthdays", help="List upcoming birthdays")
    async def list_birthdays(self, ctx):
        guild_id = str(ctx.guild.id)
        
        if guild_id not in self.birthday_data:
            await ctx.send("No birthdays recorded yet!")
            return
            
        today = date.today()
        upcoming_birthdays = []
        
        for member_id, birthday_data in self.birthday_data[guild_id]["members"].items():
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

def setup(bot):
    bot.add_cog(BirthdayTasks(bot))