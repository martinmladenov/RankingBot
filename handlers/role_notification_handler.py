import discord
from discord.ext import commands
from helpers import role_helper
import time


class RoleNotificationHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or message.channel.type != discord.ChannelType.text:
            return

        if await role_helper.should_be_notified(message.author):
            msg = await message.reply(message.author.mention + ' _You don\'t have roles! Roles unlock hidden channels '
                                                         'related to your university and programme, so you should get '
                                                         'them by going to the <#879407265336152104> channel '
                                                         'and clicking the corresponding buttons._')
            time.sleep(60)
            await msg.delete()

def setup(bot):
    bot.add_cog(RoleNotificationHandler(bot))
