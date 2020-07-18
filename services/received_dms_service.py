from datetime import datetime


class ReceivedDMsService:
    def __init__(self, db_conn):
        self.db_conn = db_conn

    async def add_dm(self, user_id: str, message: str, success: bool = None, timestamp: datetime = None):
        if timestamp is None:
            timestamp = datetime.utcnow()

        await self.db_conn.execute(
            'INSERT INTO received_dms (user_id, message, success, timestamp) VALUES ($1, $2, $3, $4)',
            user_id, message, success, timestamp)
