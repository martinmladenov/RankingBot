from discord.ext import tasks, commands
from services import dm_service


class DmReminderSenderBackgroundTask(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.send_reminders.start()

    @tasks.loop(minutes=30)
    async def send_reminders(self):
        async with (await self.bot.get_db_conn()).acquire() as connection:
            dm = dm_service.DMService(connection)
            await dm.send_all_reminder_dms(self.bot)

    @send_reminders.before_loop
    async def before_send_reminders(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(DmReminderSenderBackgroundTask(bot))
