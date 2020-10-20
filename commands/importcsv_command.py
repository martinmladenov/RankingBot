import aiohttp
from discord.ext import commands

import constants
from services import data_import_service


class ImportcsvCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def importcsv(self, ctx, source: str = None):

        if ctx.message.author.id != constants.administrator_user_id or not ctx.guild:
            await ctx.send(ctx.message.author.mention + ' You don\'t have permission to execute this command')
            return

        if len(ctx.message.attachments) != 1:
            raise commands.UserInputError

        await ctx.send(ctx.message.author.mention + ' Importing ranks...')

        async with self.bot.db_conn.acquire() as connection:
            data_import = data_import_service.DataImportService(connection)

            tr = connection.transaction()
            await tr.start()

            try:
                all_members = self.bot.get_all_members()

                attachment_url = ctx.message.attachments[0].url

                async with aiohttp.ClientSession() as session:
                    async with session.get(attachment_url) as resp:
                        csv_data = await resp.text()

                imported, skipped, unknown_user = await data_import.import_ranks_from_csv(csv_data, source, all_members)

                await tr.commit()

                await ctx.send(ctx.message.author.mention +
                               f' Imported {imported} ranks, skipped {skipped}, {unknown_user} unknown users')
            except Exception as ex:
                await tr.rollback()
                await ctx.send(ctx.message.author.mention + ' ' + str(ex))
                raise

    @importcsv.error
    async def info_error(self, ctx, error):
        user = ctx.message.author
        if isinstance(error, commands.UserInputError):
            await ctx.send(user.mention + ' Invalid arguments. Usage: `.importcsv [source]` and attach the csv file.')
        else:
            await ctx.send(user.mention + ' An unexpected error occurred')
            raise


def setup(bot):
    bot.add_cog(ImportcsvCommand(bot))
