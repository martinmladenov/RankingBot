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
