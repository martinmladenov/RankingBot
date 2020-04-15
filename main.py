from commands import clearrank_command, ranks_command, setrank_command

from discord.ext import commands
import os

bot = commands.Bot(command_prefix='.')

selection_programmes = ['tud-cse', 'tud-ae', 'tud-nb', 'tue-cse']

bot.add_cog(clearrank_command.ClearrankCommand(bot))
bot.add_cog(ranks_command.RanksCommand(bot))
bot.add_cog(setrank_command.SetrankCommand(bot, selection_programmes))


@bot.event
async def on_ready():
    print('Logged in as ' + bot.user.name)


bot.run(os.environ['DISCORD_SECRET'])
