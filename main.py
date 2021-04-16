from os import listdir
from os.path import isfile, join
from asyncio import Event
import asyncpg

from discord.ext import commands
import discord
from discord_slash import SlashCommand
import os

bot = commands.Bot(command_prefix='.', help_command=None)
slash = SlashCommand(bot, sync_commands=True)

if __name__ == '__main__':
    dirs = ['commands', 'handlers']
    for cogs_dir in dirs:
        for extension in [f.replace('.py', '') for f in listdir(cogs_dir) if isfile(join(cogs_dir, f))]:
            try:
                full_name = cogs_dir + '.' + extension
                bot.load_extension(full_name)
                print(f'Loaded {full_name}')
            except (discord.ClientException, ModuleNotFoundError):
                print(f'Failed to load extension {extension}.')


@bot.event
async def on_ready():
    print('Logged in as ' + bot.user.name)
    await bot.change_presence(activity=(discord.Game('.help | .ranks')))
    await set_up_db()


# Block threads until database is fully initialised

db_init_event = Event()


async def get_db_conn_initial():
    if not db_init_event.is_set():
        print("Database not initialised yet, waiting before processing request...")
    await db_init_event.wait()
    print("Database has finished initialising, resuming request execution")
    return await bot.get_db_conn()


async def get_db_conn_actual():
    return bot.db_conn_internal


async def set_up_db():
    bot.db_conn_internal = await asyncpg.create_pool(dsn=os.environ['DATABASE_URL'] + '?sslmode=require')
    bot.get_db_conn = get_db_conn_actual
    db_init_event.set()


bot.get_db_conn = get_db_conn_initial
bot.run(os.environ['DISCORD_SECRET'])
