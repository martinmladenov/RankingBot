from commands import clearrank_command, ranks_command, setrank_command, helprank_command, setofferdate_command

from discord.ext import commands
import discord
import os

bot = commands.Bot(command_prefix='.', help_command=None)

bot.add_cog(clearrank_command.ClearrankCommand(bot))
bot.add_cog(ranks_command.RanksCommand(bot))
bot.add_cog(setrank_command.SetrankCommand(bot))
bot.add_cog(helprank_command.HelprankCommand(bot))
bot.add_cog(setofferdate_command.SetofferdateCommand(bot))


@bot.event
async def on_ready():
    print('Logged in as ' + bot.user.name)
    await bot.change_presence(activity=(discord.Game('.helprank / .ranks')))


bot.run(os.environ['DISCORD_SECRET'])
