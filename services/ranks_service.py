from datetime import date
from utils import programmes_util
from services.errors.entry_already_exists_error import EntryAlreadyExistsError


class RanksService:
    def __init__(self, db_conn):
        self.db_conn = db_conn

    async def add_rank(self, rank: int, programme: str, user_id: str = None, offer_date: date = None):
        if rank <= 0 or rank >= 10000 or programme not in programmes_util.programmes:
            raise ValueError

        if user_id is not None:
            curr_rank = await self.db_conn.fetchrow('SELECT rank FROM ranks WHERE user_id = $1 AND programme = $2',
                                                    user_id, programme)
            if curr_rank is not None:
                raise EntryAlreadyExistsError

        if offer_date is None and rank <= programmes_util.programmes[programme].places:
            offer_date = date(2020, 4, 15)

        await self.db_conn.execute(
            'INSERT INTO ranks (user_id, rank, programme, offer_date) VALUES ($1, $2, $3, $4)',
            user_id, rank, programme, offer_date)

    async def delete_rank(self, user_id: str, programme: str):
        if programme is None:
            await self.db_conn.execute('DELETE FROM ranks WHERE user_id = $1', user_id)
        else:
            if programme not in programmes_util.programmes:
                raise ValueError
            await self.db_conn.execute('DELETE FROM ranks WHERE user_id = $1 AND programme = $2',
                                       user_id, programme)
