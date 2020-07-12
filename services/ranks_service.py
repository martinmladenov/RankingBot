from datetime import date
from utils import programmes_util
from services.errors.entry_already_exists_error import EntryAlreadyExistsError
from services.errors.date_incorrect_error import DateIncorrectError
from services.errors.entry_not_found_error import EntryNotFoundError


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

        if rank <= programmes_util.programmes[programme].places:
            if offer_date is None:
                offer_date = date(2020, 4, 15)
            else:
                raise DateIncorrectError

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

    async def set_offer_date(self, user_id: str, programme: str, offer_date: date):
        if programme not in programmes_util.programmes:
            raise ValueError

        rank = await self.db_conn.fetchval('SELECT rank FROM ranks WHERE user_id = $1 AND programme = $2',
                                           user_id, programme)

        if not rank:
            raise EntryNotFoundError

        if rank <= programmes_util.programmes[programme].places:
            raise DateIncorrectError

        await self.db_conn.execute('UPDATE ranks SET offer_date = $1 WHERE user_id = $2 AND programme = $3',
                                   offer_date, user_id, programme)

    async def get_top_ranks(self):
        rows = await self.db_conn.fetch('SELECT username, rank, programme FROM ranks '
                                        'JOIN user_data ON ranks.user_id = user_data.user_id '
                                        'WHERE (is_private IS NULL OR is_private = FALSE) AND username IS NOT NULL '
                                        'ORDER BY rank ASC')

        curr_programmes = set(map(lambda x: x[2], rows))
        grouped_ranks = [(p, [row for row in rows if row[2] == p]) for p in curr_programmes]

        grouped_ranks.sort(key=lambda g: len(g[1]), reverse=True)

        return grouped_ranks
