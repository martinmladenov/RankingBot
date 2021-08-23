from discord.ext import commands

from helpers import role_helper

import constants


class CreaterolemenuCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def createrolemenu(self, ctx, menu_type: str):

        if ctx.message.author.id != constants.administrator_user_id or not ctx.guild:
            await ctx.send(ctx.message.author.mention + ' You don\'t have permission to execute this command')
            return

        if menu_type == 'student':
            message = '**_Roles for students_**\n' \
                      '_Choose a role below if you are a current student or have been accepted._' \
                      '\n\n**Please select your study programme by clicking the button below:**'
            suffix = '-stud'
        else:
            raise commands.UserInputError

        guild_emojis = await ctx.guild.fetch_emojis()
        emoji_dict = {
            'tud': next(e for e in guild_emojis if e.name == 'TUD'),
            'tue': next(e for e in guild_emojis if e.name == 'TuE'),
            'utwente': next(e for e in guild_emojis if e.name == 'UTWENTE')
        }

        components = role_helper.generate_components(suffix, emoji_dict)

        await ctx.send(message, components=components)

    @createrolemenu.error
    async def info_error(self, ctx, error):
        user = ctx.message.author
        if isinstance(error, commands.UserInputError):
            await ctx.send(user.mention + ' Invalid arguments. Usage: `.createrolemenu <student>`')
        else:
            await ctx.send(user.mention + ' An unexpected error occurred')
            raise


def setup(bot):
    bot.add_cog(CreaterolemenuCommand(bot))
