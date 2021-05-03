from os import listdir
from os.path import isfile, join
from asyncio import Event
import asyncpg

from discord.ext import commands
import discord
from discord_slash import SlashCommand, SlashContext
import os
from dotenv import load_dotenv

# loads the dotenv variables into the environment
load_dotenv()

# if its not present in the .env then it will load it from the environ, if not present it will be set to None
SSLString = '?sslmode=require' if os.getenv(
    'SSL_MODE') == None or os.getenv('SSL_MODE') == 'True' else ''

if (os.getenv('DATABASE_URL') == None):
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_NAME = os.getenv('DB_NAME')
    os.environ['DATABASE_URL'] = f"postgres://{DB_USER}:{DB_PASSWORD}@localhost:5432/{DB_NAME}{SSLString}"
else:
    os.environ['DATABASE_URL'] = f"{os.environ['DATABASE_URL']}{SSLString}"

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
    await bot.change_presence(activity=(discord.Game('/offers | /ranks')))
    await set_up_db()


@bot.event
async def on_slash_command_error(ctx: SlashContext, ex: Exception):
    await ctx.send('An unexpected error occurred. Please try again later.')
    raise ex


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
    bot.db_conn_internal = await asyncpg.create_pool(dsn=os.environ['DATABASE_URL'])
    bot.get_db_conn = get_db_conn_actual
    db_init_event.set()


bot.get_db_conn = get_db_conn_initial
bot.run(os.environ['DISCORD_SECRET'])
