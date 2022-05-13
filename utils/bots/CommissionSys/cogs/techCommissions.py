from typing import Literal

import discord
from discord import ui, app_commands
from discord.ext import commands, tasks

from core import database
from core.checks import is_botAdmin
from core.common import TechID, Emoji, StaffID


class BotRequestModal(ui.Modal, title="Bot Development Request"):
    def __init__(self, bot: commands.Bot, extguild: bool = False, responseid: int = None) -> None:
        super().__init__(timeout=None)
        self.bot = bot
        self.extguild = extguild
        self.responseid = responseid

    titleTI = ui.TextInput(
        label="What is a descriptive title for your project?",
        style=discord.TextStyle.long,
        max_length=1024,
    )

    teamTI = ui.TextInput(
        label="Which team is this project for?",
        style=discord.TextStyle.short,
        max_length=1024,
    )

    descriptionTI = ui.TextInput(
        label="Write a brief description of the project.",
        style=discord.TextStyle.long,
        max_length=1024,
    )

    approvalTI = ui.TextInput(
        label="Do you have approval for this commission?",
        style=discord.TextStyle.long,
        max_length=1024,
    )

    anythingElseTI = ui.TextInput(
        label="Anything else?",
        style=discord.TextStyle.long,
        required=False,
        max_length=1024,
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            content="Got it! Please wait while I create your ticket.", ephemeral=True
        )

        embed = discord.Embed(
            title="Bot Developer Commission", color=discord.Color.blurple()
        )
        embed.set_author(
            name=interaction.user.name, icon_url=interaction.user.avatar.url
        )
        embed.add_field(name="Project Title", value=self.titleTI.value, inline=False)
        embed.add_field(name="Team Requester", value=self.teamTI.value, inline=False)
        embed.add_field(
            name="Project Description", value=self.descriptionTI.value, inline=False
        )
        embed.add_field(name="Approval", value=self.approvalTI.value, inline=False)
        embed.add_field(
            name="Anything else?", value=f"E: {self.anythingElseTI.value}", inline=False
        )
        embed.set_footer(text="Bot Developer Commission")

        c_ch: discord.TextChannel = self.bot.get_channel(TechID.ch_bot_requests)
        msg: discord.Message = await c_ch.send(interaction.user.mention, embed=embed)
        thread = await msg.create_thread(name=self.titleTI.value)

        await thread.send(
            f"{interaction.user.mention} has requested a bot development project.\n<@&{TechID.r_bot_developer}>"
        )
        if self.extguild:
            resp_channel = self.bot.get_channel(self.responseid)
            await resp_channel.send(
                f"{interaction.user.mention} your commission has been opened!\nYou can view it here: <#{thread.id}>",
                delete_after=10.0
            )


class CommissionTechButton(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.value = None
        self.bot = bot

    @discord.ui.button(
        label="Start Commission",
        style=discord.ButtonStyle.blurple,
        custom_id="persistent_view:tech_pjt",
        emoji="📝",
    )
    async def verify(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        extguild = False
        if interaction.guild.id == StaffID.g_staff_resources:
            guild = self.bot.get_guild(TechID.g_tech)
            if guild.get_member(interaction.user.id) is not None:
                extguild = True
            else:
                return await interaction.followup.send(
                    f"{interaction.user.mention} you aren't in the IT server, please join the server and try again.",
                    ephemeral=True
                )

        modal = BotRequestModal(self.bot, extguild, interaction.channel.id)
        return await interaction.response.send_modal(modal)


class TechProjectCMD(commands.Cog):
    """
    Commands for bot commissions
    """

    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.__cog_name__ = "Bot Commissions"
        self.autoUnarchiveThread.start()

    @property
    def display_emoji(self) -> str:
        return Emoji.pythonLogo

    async def cog_unload(self):
        self.autoUnarchiveThread.cancel()

    @commands.command()
    @is_botAdmin
    async def techEmbed(self, ctx):
        embed = discord.Embed(
            title="Bot Developer Commissions", color=discord.Color.brand_green()
        )
        embed.add_field(
            name="Get Started",
            value="To get started, click the button below!\n*Please make sure you are authorized to make commissions!*",
        )
        embed.set_footer(
            text="The Bot Development Team has the right to cancel and ignore any commissions if deemed appropriate. "
            "We also have the right to cancel and ignore any commissions if an improper deadline is given, "
            "please make sure you create a commission ahead of time and not right before a due date",
        )
        view = CommissionTechButton(self.bot)
        await ctx.send(embed=embed, view=view)

    @app_commands.command()
    @app_commands.guilds(TechID.g_tech)
    @app_commands.checks.cooldown(1, 300, key=lambda i: (i.guild_id, i.channel.id))
    async def commission(
        self, interaction: discord.Interaction, action: Literal["close"]
    ):
        channel: discord.TextChannel = self.bot.get_channel(TechID.ch_bot_requests)
        thread = interaction.channel

        if not isinstance(thread, discord.Thread):
            await interaction.response.send_message(
                "This is not a bot commission.", ephemeral=True
            )
            return

        if action == "close":
            query = database.TechCommissionArchiveLog.select().where(
                database.TechCommissionArchiveLog.ThreadID == thread.id
            )
            if thread not in channel.threads or query.exists():
                await interaction.response.send_message(
                    "This commission is already closed.", ephemeral=True
                )
                return
            else:
                query = database.TechCommissionArchiveLog.create(ThreadID=thread.id)
                query.save()

                await interaction.response.send_message(
                    "Commission closed! You can find the commission in the archived threads of that channel."
                )
                await thread.edit(archived=True)

    @commands.Cog.listener("on_message")
    async def auto_open_commission(self, message: discord.Message):
        channel: discord.TextChannel = self.bot.get_channel(TechID.ch_bot_requests)

        if (
            isinstance(message.channel, discord.Thread)
            and message.type == discord.MessageType.default
            and message.channel in channel.threads
        ):

            query = database.TechCommissionArchiveLog.select().where(
                database.TechCommissionArchiveLog.ThreadID == message.channel.id
            )
            if query.exists():
                result = query.get()
                result.delete_instance()

                await message.reply(content="Commission re-opened!")

    @commands.command()
    async def leadershipPost(self, ctx: commands.Context):
        """
        Post the Bot Development Commission Process in the leadership server.
        """
        await ctx.send("https://cdn.discordapp.com/attachments/956619270899499028/956625228371492885/4.png\n\n")
        await ctx.send(
            "** **\n\n**Bot Development Commission Process**\n"
            "Information Technology is able to help automate and improve School Simplified through technology. If you "
            "have an idea that could improve your team's or School Simplified's operation, feel free to make a "
            "commission!\n\n"
            "*Join the IT server (https://discord.gg/WugSf4a74a) and click the button to create a Developer"
            "Commission (bot creation, bot changes).*",
            view=CommissionTechButton(self.bot)
        )

    @tasks.loop(seconds=60.0)
    async def autoUnarchiveThread(self):
        """
        Creates a task loop to make sure threads don't automatically archive due to inactivity.
        """

        channel: discord.TextChannel = self.bot.get_channel(TechID.ch_bot_requests)
        query = database.TechCommissionArchiveLog.select()
        closed_threads = [entry.ThreadID for entry in query]

        async for archived_thread in channel.archived_threads():
            if archived_thread.id not in closed_threads:
                await archived_thread.edit(archived=False)

    @autoUnarchiveThread.before_loop
    async def before_loop_(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    await bot.add_cog(TechProjectCMD(bot))