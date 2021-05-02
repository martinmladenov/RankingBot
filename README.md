# RankingNumberBot

**Running bot locally**
1. create a local postgresql database
2. set up the database by running the stuff in the sql_setup.sql file using your favourite database management software 
3. set the DATABASE_URL environment variable to the correct connection string and remove + '?sslmode=require' from line 57 of main.py (since you most likely don't have an SSL certificate set up locally)
4. create a discord app on https://discord.com/developers and create a bot user too
5. set the DISCORD_SECRET environment variable to the bot token (not the application token)
6. change the configuration in constants.py (optional, only needed for very few features/commands)
7. install dependencies usinhg "pip install -r requirements.txt"
8. run main.py and enjoy
