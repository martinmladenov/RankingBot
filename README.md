# RankingBot

**Running bot locally**
1. Create a local PostgreSQL database
2. Set up the database by running the commands in the `sql_setup.sql` file using your favourite database management software
3. Copy `.env.example` into a `.env` file
4. Set environment variables `DB_USER`, `DB_PASSWORD` and `DB_NAME`
   - If desired, you can set the `DATABASE_URL` environment variable to the connection string containing the username, password, database name, hostname and port instead
   - Keep `SSL_MODE` set to false when running the bot locally, unless you need it
       - If `SSL_MODE` is missing from `.env`, it will default to using SSL
5. Create Discord application at https://discord.com/developers and add a bot user
6. Set the `DISCORD_SECRET` environment variable to the bot token (not the application token)
7. Set the `GUILD_IDS` environment variable to the id of your server to force Discord to register the commands more quickly
8. Change the configuration in `constants.py` (optional, only needed for very few features/commands such as setting the current academic year or changing the administrative user)
9. Install dependencies using `pip install -r requirements.txt`
10. Run main.py and enjoy

**Deploying bot**
   - Environment variables need to be set for `DATABASE_URL` and `DISCORD_SECRET` 
       - If `SSL_MODE` is missing from `.env`, it will default to using SSL
