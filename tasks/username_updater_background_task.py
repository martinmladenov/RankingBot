from discord.ext import tasks, commands
from services import user_data_service
import os


class UsernameUpdaterBackgroundTask(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        if os.getenv('SERVER_ID'):
            self.update_usernames.start()

    @tasks.loop(hours=12)
    async def update_usernames(self):
        async with (await self.bot.get_db_conn()).acquire() as connection:
            users_service = user_data_service.UserDataService(connection)
            users = await users_service.get_all_users()

            try:
                guild = await self.bot.fetch_guild(os.getenv('SERVER_ID'))
                guild_members = dict(map(lambda x: (str(x.id), x.name),
                                         await guild.fetch_members(limit=10000).flatten()))
            except:
                print('Warning: Could not update usernames - unable to fetch guild members.')
                return

            for user in users:
                user_id = user[0]
                stored_username = user[1]

                if user_id not in guild_members.keys():
                    # print(f'user {stored_username} ({user_id}) not in guild')
                    continue

                actual_username = guild_members[user_id]

                if stored_username == actual_username:
                    continue

                await users_service.set_username(user_id, actual_username)

                print(f'Updated username for user {user_id}: {stored_username} -> {actual_username}')

    @update_usernames.before_loop
    async def before_printer(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(UsernameUpdaterBackgroundTask(bot))
