# tasks.py
from discord.ext import commands, tasks
from datetime import date, datetime
import discord, pytz, json, os

class BirthdayTasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.birthday_data = {}

    def _parse_birthday(self, date_str):
        """Parse birthday date string in various formats"""
        try:
            # Try ISO format first (YYYY-MM-DD)
            return date.fromisoformat(date_str)
        except ValueError:
            try:
                # Try MM-DD format
                month, day = map(int, date_str.split('-'))
                return date(2024, month, day)
            except ValueError:
                raise ValueError(f"Invalid birthday format: {date_str}")
    
    @tasks.loop(hours=24)
    async def check_birthdays(self):
        """Check for birthdays every 24 hours"""
        await self.bot.wait_until_ready()
        if not self.bot.is_closed():
            today = date.today()
            for guild_id, guild_data in self.birthday_data.items():
                guild = self.bot.get_guild(int(guild_id))
                if not guild:
                    continue
                
                for member_id, birthday in guild_data["members"].items():
                    try:
                        bday_date = self._parse_birthday(birthday["date"])
                        if today.month == bday_date.month and \
                           today.day == bday_date.day:
                            print(f"Happy birthday to {birthday['username']} in {guild.name}!")
                            await self.create_birthday_event(guild, bday_date)
                    except ValueError as e:
                        print(f"Invalid birthday format for {birthday['username']}: {str(e)}")
            
            # await asyncio.sleep(86400)  # 24 hours

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

    @commands.command(name="checkbirthdays", description="Check for birthdays manually")
    async def check_birthdays_manually(self, ctx):
        """Check for birthdays manually"""
        await self.check_birthdays()

    @commands.command(name="ping", help="Check the bot's latency")
    async def ping(self, ctx):
        """Check the bot's latency"""
        latency = self.bot.latency * 1000  # Convert to milliseconds
        await ctx.send(f"Pong! The bot's latency is {latency:.2f}ms")

    @commands.command(name="setbirthday", description="Set your birthday")
    async def set_birthday(self, ctx, month: int, day: int):
        if not (1 <= month <= 12 and 1 <= day <= 31):
            await ctx.send("Invalid date! Please use MM DD format.")
            return
            
        try:
            current_year = datetime.now().year + 1
            # Validate date exists
            dt = date(current_year, month, day)
            start = pytz.utc.localize(datetime.combine(dt, datetime.min.time()))
            end = pytz.utc.localize(datetime.combine(dt, datetime.max.time()))
            
            guild_id = str(ctx.guild.id)
            member_id = str(ctx.author.id)
            
            if guild_id not in self.birthday_data:
                self.birthday_data[guild_id] = {"members": {}}
                
            # Store in ISO format (YYYY-MM-DD)
            iso_date = f"{current_year}-{month:02d}-{day:02d}"
            self.birthday_data[guild_id]["members"][member_id] = {
                "date": iso_date,
                "username": ctx.author.name,
                "discriminator": ctx.author.discriminator
            }
            
            # Save data
            with open("birthdays.json", "w") as f:
                json.dump(self.birthday_data, f)

            event_exists = False
            for event in ctx.guild.scheduled_events:
                if event.name == f"Happy Birthday {ctx.author.name}":
                    event_exists = True
                    break
            
            if not event_exists:
                event = await ctx.guild.create_scheduled_event(
                    name=f"Happy Birthday {ctx.author.name}",
                    description=f"Join us in celebrating {ctx.author.name}'s birthday!",
                    start_time=start,
                    end_time=end,
                    privacy_level=discord.PrivacyLevel.guild_only,
                    location="Discord",
                    entity_type=discord.EntityType.external,
                    reason="Created by birthday bot"
                )
                await ctx.send(f"🎉 An event for your birthday has been created! Check it out above.")
                
            await ctx.send(f"🎂 Your birthday has been set to {month}/{day}")
            
        except ValueError as err:
            print(err)
            await ctx.send("Invalid date! Please check the month and day.")

    @commands.command(name="listbirthdays", description="List upcoming birthdays")
    async def list_birthdays(self, ctx):
        guild_id = str(ctx.guild.id)
        
        if guild_id not in self.birthday_data:
            await ctx.send("No birthdays recorded yet!")
            return
            
        today = date.today()
        upcoming_birthdays = []
        
        for member_id, birthday_data in self.birthday_data[guild_id]["members"].items():
            try:
                bday_date = self._parse_birthday(birthday_data["date"])
                
                # Calculate days until birthday
                next_birthday = date(today.year, bday_date.month, bday_date.day)
                if next_birthday < today:
                    next_birthday = date(today.year + 1, bday_date.month, bday_date.day)
                
                days_until = (next_birthday - today).days
                
                username = f"{birthday_data['username']}#{birthday_data['discriminator']}"
                upcoming_birthdays.append(f"{username}: {days_until} days until birthday")
            except ValueError as e:
                print(f"Skipping invalid birthday for {birthday_data['username']}: {str(e)}")
        
        if not upcoming_birthdays:
            await ctx.send("No upcoming birthdays!")
        else:
            await ctx.send("\n".join(upcoming_birthdays))

async def setup(bot):
    await bot.add_cog(BirthdayTasks(bot))