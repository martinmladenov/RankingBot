from discord.ext import commands
from discord_slash import SlashContext
from discord_slash.cog_ext import cog_slash as slash
from discord_slash.utils.manage_commands import create_option
from utils import command_option_type
import re

from services import ranks_service, user_data_service
from services.errors.entry_already_exists_error import EntryAlreadyExistsError
from helpers import programmes_helper
import constants


class GetrankCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash(name="getrank",
           description="Get the ranking number of the specified user",
           options=[
               create_option(
                   name="user",
                   description="The user",
                   option_type=command_option_type.STRING,
                   required=True
               ),
               create_option(
                   name='programme',
                   description='Study programme',
                   option_type=command_option_type.STRING,
                   required=False,
                   choices=programmes_helper.get_programme_choices()
               )
           ])
    async def get_rank(self, ctx: SlashContext, user: str, programme: str = None):
        async with (await self.bot.get_db_conn()).acquire() as connection:
            user_id = re.sub(r"[<@!>]", "", user)

            if not user_id.isdigit():
                await ctx.send(ctx.author.mention + "Invalid user")
                return

            users = user_data_service.UserDataService(connection)
            res = await users.get_user_rank(user_id)

            if res and res[0]:
                is_private, rank = res[0]

                if is_private:
                    await ctx.send(ctx.author.mention + f"User {user} has a private rank.")
                else:
                    await ctx.send(ctx.author.mention + f"User {user} is ranked {rank}.")
            else:
                await ctx.send(ctx.author.mention +
                               f"User {user} is either invalid or has not posted his ranking number.")

        return None


def setup(bot):
    bot.add_cog(GetrankCommand(bot))
