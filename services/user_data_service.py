class UserDataService:
    def __init__(self, db_conn):
        self.db_conn = db_conn

    async def add_user(self, user_id: str, username: str) -> bool:
        user_data_row = await self.db_conn.fetchrow('SELECT user_id FROM user_data WHERE user_id = $1',
                                                    user_id)
        if user_data_row:
            return False

        await self.db_conn.execute('INSERT INTO user_data (user_id, username) VALUES ($1, $2)',
                                   user_id, username)

        return True

    async def get_all_users(self):
        users = await self.db_conn.fetch('SELECT user_id, username FROM user_data')
        return users

    async def get_user_ranks(self, user_id: str):
        user = await self.db_conn.fetch('SELECT is_private, rank, year, programme FROM ranks WHERE user_id = $1', user_id)
        return user

    async def set_username(self, user_id: str, new_username: str):
        await self.db_conn.execute('UPDATE user_data SET username = $1 WHERE user_id = $2',
                                   new_username, user_id)
