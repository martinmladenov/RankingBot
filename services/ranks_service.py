from datetime import date
from helpers import programmes_helper
from services.errors.entry_already_exists_error import EntryAlreadyExistsError
from services.errors.date_incorrect_error import DateIncorrectError
from services.errors.entry_not_found_error import EntryNotFoundError
import constants

class RanksService:
    def __init__(self, db_conn):
        self.db_conn = db_conn

    async def add_rank(self, rank: int, programme: str, user_id: str = None, offer_date: date = None,
                       source: str = None):
        if rank <= 0 or rank >= 10000 or programme not in programmes_helper.programmes:
            raise ValueError

        if user_id is not None:
            curr_rank = await self.db_conn.fetchrow('SELECT rank FROM ranks WHERE user_id = $1 AND programme = $2',
                                                    user_id, programme)
            if curr_rank is not None:
                raise EntryAlreadyExistsError

        if rank <= programmes_helper.programmes[programme].places:
            if offer_date is None:
                offer_date = date(year, 4, 15)
            else:
                raise DateIncorrectError

        await self.db_conn.execute(
            'INSERT INTO ranks (user_id, rank, programme, offer_date, source) VALUES ($1, $2, $3, $4, $5)',
            user_id, rank, programme, offer_date, source)

    async def delete_rank(self, user_id: str, programme: str):
        if programme is None:
            await self.db_conn.execute('DELETE FROM ranks WHERE user_id = $1', user_id)
        else:
            if programme not in programmes_helper.programmes:
                raise ValueError
            await self.db_conn.execute('DELETE FROM ranks WHERE user_id = $1 AND programme = $2',
                                       user_id, programme)

    async def set_offer_date(self, user_id: str, programme: str, offer_date: date):
        if programme not in programmes_helper.programmes:
            raise ValueError

        rank = await self.db_conn.fetchval('SELECT rank FROM ranks WHERE user_id = $1 AND programme = $2',
                                           user_id, programme)

        if not rank:
            raise EntryNotFoundError

        if rank <= programmes_helper.programmes[programme].places:
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

    async def get_is_private(self, user_id: str) -> bool:
        is_private = await self.db_conn.fetchval('SELECT is_private FROM ranks '
                                                 'WHERE user_id = $1',
                                                 user_id)
        return is_private

    async def get_has_only_one_rank(self, user_id: str) -> bool:
        is_private = await self.db_conn.fetchval('SELECT COUNT(is_private) FROM ranks '
                                                 'WHERE user_id = $1',
                                                 user_id)
        return is_private == 1

    async def get_is_private_programme(self, user_id: str, programme: str) -> bool:
        if programme not in programmes_helper.programmes:
            raise ValueError

        is_private = await self.db_conn.fetchval('SELECT is_private FROM ranks '
                                                 'WHERE user_id = $1 AND programme = $2',
                                                 user_id, programme)
        return is_private

    async def set_is_private(self, user_id: str, is_private: bool):
        await self.db_conn.execute('UPDATE ranks SET is_private = $1 '
                                   'WHERE user_id = $2',
                                   is_private, user_id)

    async def set_is_private_programme(self, user_id: str, is_private: bool, programme: str):
        await self.db_conn.execute('UPDATE ranks SET is_private = $1 '
                                   'WHERE user_id = $2 AND programme = $3',
                                   is_private, user_id, programme)
