from os import listdir
from os.path import isfile, join
import asyncpg

from discord.ext import commands
import discord
import os

bot = commands.Bot(command_prefix='.', help_command=None)

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


async def set_up_db():
    bot.db_conn = await asyncpg.create_pool(dsn=os.environ['DATABASE_URL'] + '?sslmode=require')

create table ranks

(

    id         serial primary key,

    user_id    varchar(50),

    rank       int         not null,

    programme  varchar(15) not null,

    offer_date DATE,

    UNIQUE (user_id, programme)

);

create table user_data

(

    id         serial primary key unique,

    user_id    varchar(50) unique not null,

    username   varchar(50)        not null,

    is_private boolean            not null default false,

    dm_programme varchar(15),

    dm_status int,

    dm_last_sent timestamp

);

create table received_dms

(

    id        serial primary key,

    user_id   varchar(50) not null,

    message   varchar(400),

    success   boolean,

    timestamp timestamp

);

create table excluded_programmes

(

    id        serial primary key,

    user_id   varchar(50) not null,

    programme varchar(15) not null

)
    
bot.run(os.environ['DISCORD_SECRET'])
