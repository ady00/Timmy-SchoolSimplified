import time
import discord
import pytz
from core import database
from core.common import Others
from discord.ext import commands
from datetime import datetime


class TutorMain(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.RepeatEmoji = {False: "\U00002b1b", True: "🔁"}

    @commands.command()
    async def view(self, ctx, id=None):
        if id is None:
            query: database.TutorBot_Sessions = (
                database.TutorBot_Sessions.select().where(
                    database.TutorBot_Sessions.TutorID == ctx.author.id
                )
            )

            embed = discord.Embed(
                title="Scheduled Tutor Sessions", color=discord.Color.dark_blue()
            )
            embed.add_field(name="Schedule:", value=f"{ctx.author.name}'s Schedule:")

            if query.count() == 0:
                embed.add_field(
                    name="List:", value="You have no tutor sessions yet!", inline=False
                )

            else:
                ListTen = []
                i = 0
                for entry in query:
                    entry: database.TutorBot_Sessions = entry
                    DateOBJ = pytz.timezone("America/New_York").localize(entry.Date)
                    if not isinstance(DateOBJ, datetime):
                        DateOBJ = datetime.fromisoformat(DateOBJ)

                    result = datetime.strftime(DateOBJ, "%B %d, %Y | %I:%M %p EST")
                    studentUser = await self.bot.fetch_user(entry.StudentID)
                    ListTen.append(
                        f"{self.RepeatEmoji[entry.Repeat]} `{entry.SessionID}`- - {result} -> {studentUser.name}"
                    )

                embed.add_field(name="List:", value="\n".join(ListTen), inline=False)
            embed.set_thumbnail(url=Others.timmyTeacher_png)
            await ctx.send(embed=embed)

        else:
            entry = database.TutorBot_Sessions.select().where(
                database.TutorBot_Sessions.SessionID == id
            )
            if entry.exists():
                entry = entry.get()

                studentUser = await self.bot.fetch_user(entry.StudentID)

                date = entry.Date.strftime("%m/%d/%Y")
                amORpm = entry.Date.strftime("%p")

                embed = discord.Embed(
                    title="Tutor Session Query",
                    description=f"Here are the query results for {id}",
                )
                embed.add_field(
                    name="Values",
                    value=f"**Session ID:** `{entry.SessionID}`"
                    f"\n**Student:** `{studentUser.name}`"
                    f"\n**Tutor:** `{ctx.author.name}`"
                    f"\n**Date:** `{date}`"
                    f"\n**Time:** `{entry.Time}`"
                    f"\n**Repeat?:** {self.RepeatEmoji[entry.Repeat]}",
                )
                embed.set_footer(text=f"Subject: {entry.Subject}")
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(
                    title="Invalid Session",
                    description="This session does not exist, please check the ID you've provided!",
                    color=discord.Color.red(),
                )
                await ctx.send(embed=embed)

    @commands.command()
    @commands.has_any_role("Senior Tutor", "Tutoring Manager", "Tutoring Director")
    async def mview(self, ctx, user: discord.User):
        """
        View someone else's tutor sessions
        """
        query: database.TutorBot_Sessions = database.TutorBot_Sessions.select().where(
            database.TutorBot_Sessions.TutorID == user.id
        )

        embed = discord.Embed(
            title="Scheduled Tutor Sessions", color=discord.Color.dark_blue()
        )
        embed.add_field(name="Schedule:", value=f"{user.name}'s Schedule:")

        if query.count() == 0:
            embed.add_field(
                name="List:", value="This user has no tutor sessions yet!", inline=False
            )

        else:
            ListTen = []
            i = 0
            for entry in query:
                entry: database.TutorBot_Sessions = entry
                DateOBJ = pytz.timezone("America/New_York").localize(entry.Date)
                if not isinstance(DateOBJ, datetime):
                    DateOBJ = datetime.fromisoformat(DateOBJ)

                result = datetime.strftime(DateOBJ, "%B %d, %Y | %I:%M %p EST")
                studentUser = await self.bot.fetch_user(entry.StudentID)
                ListTen.append(
                    f"{self.RepeatEmoji[entry.Repeat]} `{entry.SessionID}`- - {result} -> {studentUser.name}"
                )

            embed.add_field(name="List:", value="\n".join(ListTen), inline=False)
        embed.set_thumbnail(url=Others.timmyTeacher_png)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(TutorMain(bot))
