# RankingNumberBot

**Running bot locally**
1. create a local postgresql database
2. set up the database by running the stuff in the sql_setup.sql file using your favourite database management software
3. copy .env.example into a .env file
4. set environment variables POSTGRESS_USER, DB_PASSWORD and DB_NAME
   - if desired you can set the DATABASE_URL environment variable to the correct connection string
   - keep SSL_MODE at false, unless you need it
5. create a discord app on https://discord.com/developers and create a bot user too
6. set the DISCORD_SECRET environment variable to the bot token (not the application token)
7. set the GUILD_IDS environment variable to the id of your server for faster development
8. change the configuration in constants.py (optional, only needed for very few features/commands)
9. install dependencies usinhg "pip install -r requirements.txt"
10. run main.py and enjoy
