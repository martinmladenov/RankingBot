from commands import clearrank_command, ranks_command, setrank_command, helprank_command, setofferdate_command, \
    toggleprivaterank_command, sendaccepteddm_command, addmanualdate_command, offers_command

from handlers import dm_handler

from discord.ext import commands
import discord
import os

bot = commands.Bot(command_prefix='.', help_command=None)

bot.add_cog(clearrank_command.ClearrankCommand(bot))
bot.add_cog(ranks_command.RanksCommand(bot))
bot.add_cog(setrank_command.SetrankCommand(bot))
bot.add_cog(helprank_command.HelprankCommand(bot))
bot.add_cog(setofferdate_command.SetofferdateCommand(bot))
bot.add_cog(toggleprivaterank_command.ToggleprivaterankCommand(bot))
bot.add_cog(sendaccepteddm_command.SendaccepteddmCommand(bot))
bot.add_cog(addmanualdate_command.AddmanualdateCommand(bot))
bot.add_cog(offers_command.OffersCommand(bot))

bot.add_cog(dm_handler.DmHandler(bot))


@bot.event
async def on_ready():
    print('Logged in as ' + bot.user.name)
    await bot.change_presence(activity=(discord.Game('.helprank / .ranks')))


bot.run(os.environ['DISCORD_SECRET'])
