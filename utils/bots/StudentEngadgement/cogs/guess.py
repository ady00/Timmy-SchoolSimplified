import discord
from discord import slash_command
from discord.ext import commands
from core.common import MAIN_ID


class Engagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(
        name="puzzle_guess",
        guild_ids=[MAIN_ID.g_main],
    )
    async def _guess(self, ctx: discord.ApplicationContext, guess: str):
        """
        :param guess: The guess you are making to the weekly puzzle
        """
        embed = discord.Embed(
            color=0xC387FF,
            title="Puzzle Guess",
            description=f"```{guess}```",
            timestamp=discord.utils.utcnow(),
        )
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar.url)

        # ssd: discord.Guild = self.bot.get_guild(950799439625355294)
        # if not ssd:
        # ssd = await self.bot.fetch_guild(950799439625355294)
        # guess_channel: discord.TextChannel = ssd.get_channel(950083341967843398)
        # if not guess_channel:
        guess_channel = await self.bot.fetch_channel(950083341967843398)
        await guess_channel.send(embed=embed)
        await ctx.respond("Your guess has been submitted!", ephemeral=True)


def setup(bot):
    bot.add_cog(Engagement(bot))
