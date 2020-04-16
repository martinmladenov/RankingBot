from commands import clearrank_command, ranks_command, setrank_command, helprank_command

from discord.ext import commands
import discord
import os

bot = commands.Bot(command_prefix='.', help_command=None)

selection_programmes = ['tud-cse', 'tud-ae', 'tud-nb', 'tue-cse']

bot.add_cog(clearrank_command.ClearrankCommand(bot))
bot.add_cog(ranks_command.RanksCommand(bot, selection_programmes))
bot.add_cog(setrank_command.SetrankCommand(bot, selection_programmes))
bot.add_cog(helprank_command.HelprankCommand(bot, selection_programmes))


@bot.event
async def on_ready():
    print('Logged in as ' + bot.user.name)
    await bot.change_presence(activity=(discord.Game('.helprank / .ranks')))


bot.run(os.environ['DISCORD_SECRET'])
