from discord.ext import commands

from services import ranks_service, user_data_service
from services.errors.entry_already_exists_error import EntryAlreadyExistsError
from utils import programmes_util


class SetrankCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def setrank(self, ctx, rank_number: int, programme: str):
        user = ctx.message.author
        user_id = str(user.id)

        async with self.bot.db_conn.acquire() as connection:
            ranks = ranks_service.RanksService(connection)
            users = user_data_service.UserDataService(connection)

            tr = connection.transaction()
            await tr.start()

            try:
                try:
                    await ranks.add_rank(rank_number, programme, user_id)
                except ValueError:
                    raise commands.UserInputError
                except EntryAlreadyExistsError:
                    await ctx.send(user.mention + ' You have already set your ranking number. To set a different one, '
                                                  f'clear it using `.clearrank {programme}` and try setting it again.')
                    await tr.rollback()
                    return

                await users.add_user(user_id, user.name)

            except:
                await tr.rollback()
                raise

            await tr.commit()
        await ctx.send(user.mention + ' Rank set.')

    @setrank.error
    async def info_error(self, ctx, error):
        user = ctx.message.author
        if isinstance(error, commands.UserInputError):
            await ctx.send(
                user.mention + f' Invalid arguments. Usage: `.setrank <rank> <{programmes_util.get_ids_string()}>`')
        else:
            await ctx.send(user.mention + ' An unexpected error occurred')
            raise


def setup(bot):
    bot.add_cog(SetrankCommand(bot))
