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
            message = '\U0001f393 **_Roles for students_**\n' \
                      '_Choose a role below if you are a current student or have been accepted._' \
                      '\n\n**Please select your study programme by clicking a button below:**'
            suffix = '-stud'
        elif menu_type == 'applicant':
            message = '\U0001f4a1 **_Roles for applicants_**\n' \
                      '_Choose a role below if you are an applicant._' \
                      '\n\n**Please select your study programme by clicking a button below:**\n' \
                      '_(you can choose more than one programme by clicking on multiple buttons)_'
            suffix = '-app'
        elif menu_type == 'accepted':
            message = '\U0001f4ec **_Roles for accepted applicants_**\n' \
                      '_Choose a role below if you are an applicant who has just been **accepted** to a programme._' \
                      '\n\n**Please select your study programme by clicking a button below:**\n' \
                      '_(you can choose more than one programme by clicking on multiple buttons)_'
            suffix = '-acc'
        elif menu_type == 'remove':
            components = role_helper.generate_components_remove_roles()
            await ctx.send(components=components)
            return
        else:
            raise commands.UserInputError

        guild_emojis = await ctx.guild.fetch_emojis()
        emoji_dict = {
            'tud': next(e for e in guild_emojis if e.name == 'tudelft_white'),
            'tue': next(e for e in guild_emojis if e.name == 'tueindhoven_white'),
            'utwente': next(e for e in guild_emojis if e.name == 'utwente_white')
        }

        components = role_helper.generate_components(suffix, emoji_dict)

        await ctx.send(message, components=components)

    @createrolemenu.error
    async def info_error(self, ctx, error):
        user = ctx.message.author
        if isinstance(error, commands.UserInputError):
            await ctx.send(user.mention + ' Invalid arguments. Usage: `.createrolemenu <student/applicant>`')
        else:
            await ctx.send(user.mention + ' An unexpected error occurred')
            raise


def setup(bot):
    bot.add_cog(CreaterolemenuCommand(bot))
