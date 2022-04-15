import discord
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
                   option_type=command_option_type.USER,
                   required=True
               ),
               create_option(
                   name='programme',
                   description='Study programme',
                   option_type=command_option_type.STRING,
                   required=False,
                   choices=programmes_helper.get_programme_choices()
               ),
               create_option(
                   name='year',
                   description='Application Year',
                   option_type=command_option_type.INTEGER,
                   required=False,
                   choices=programmes_helper.get_year_choices()
               )
           ])
    async def get_rank(self, ctx: SlashContext, user: discord.User, programme: str = None,
                       year: int = None):
        user_id = str(user.id)

        async with (await self.bot.get_db_conn()).acquire() as connection:
            users = user_data_service.UserDataService(connection)
            res = await users.get_user_ranks(user_id)

        if res:
            # Filter by is_private
            res = filter(lambda x: not x[0], res)

            # Filter by programme
            if programme:
                res = filter(lambda x: x[3] == programme, res)

            # Filter by year
            if year:
                res = filter(lambda x: x[2] == year, res)

            res = list(res)

            res.sort(key=lambda x: x[1])

            res = "\n".join(map(lambda x: f"Rank {x[1]} in {x[3]} {x[2]}", res))

            if len(res) == 0:
                await ctx.send(f"User {user} does not have recorded data that matches your filters")
            else:
                await ctx.send(f"User {user}:\n\n" + res)

        else:
            await ctx.send(f"User {user} has not posted their ranking number.")


def setup(bot):
    bot.add_cog(GetrankCommand(bot))
