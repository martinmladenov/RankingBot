import discord
from discord.ext import commands
import constants
from services import dm_service


class ReactionHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.message_id != constants.accepted_message_id:
            return

        async with self.bot.db_conn.acquire() as connection:
            dm = dm_service.DMService(connection)
            await dm.handle_reaction(payload.member, payload.emoji.name)


def setup(bot):
    bot.add_cog(ReactionHandler(bot))
