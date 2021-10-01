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
               ),
               create_option(
                   name='year',
                   description='Application Year',
                   option_type=command_option_type.INTEGER,
                   required=False,
                   choices=programmes_helper.get_year_choices()
               )
           ])
    async def get_rank(self, ctx: SlashContext, user: str, programme: str = None, year: int = constants.current_year):
        async with (await self.bot.get_db_conn()).acquire() as connection:
            user_id = re.sub(r"[<@!>]", "", user)

            if not user_id.isdigit():
                await ctx.send(ctx.author.mention + "Invalid user")
                return

            users = user_data_service.UserDataService(connection)
            res = await users.get_user_rank(user_id)

            if res:
                # Filter by programme
                if programme:
                    res = filter(lambda x: True if x[3] == programme else False, res)

                # Filter by year
                res = filter(lambda x: True if x[2] == year else False, res)
                # Filter by is_private
                res = list(filter(lambda x: True if not x[0] else False, res))

                res.sort(key=lambda x: x[1])

                res = "\n".join(map(lambda x: f"Rank: {x[1]} in {x[3]} {x[2]}", res))

                if len(res) == 0:
                    await ctx.send(ctx.author.mention + f" User {user} does not have recorded data that matches your filters")
                else:
                    await ctx.send(ctx.author.mention + f"User {user}: \n" + res)

            else:
                await ctx.send(ctx.author.mention +
                               f"User {user} is either invalid or has not posted his ranking number.")

        return None


def setup(bot):
    bot.add_cog(GetrankCommand(bot))
