from discord.utils import get

from helpers import programmes_helper
from services import ranks_service, user_data_service
from services.errors.entry_already_exists_error import EntryAlreadyExistsError
from utils import offer_date_util


class DataImportService:
    def __init__(self, db_conn):
        self.db_conn = db_conn

    async def import_ranks_from_csv(self, csv_data: str, source: str, all_members):
        """
        This method imports data into "ranks" in the following format:
        programme_id(str),ranking_number(int),offer_date(dd/mm),is_private(bool),discord_tag(Optional;User#1234)
        :param csv_data: The rows of the CSV, separated by '\n'
        :param all_members: bot.get_all_members()
        :param source: data source
        :return: None
        """

        ranks = ranks_service.RanksService(self.db_conn)
        users = user_data_service.UserDataService(self.db_conn)

        rows = csv_data.split('\n')

        i = 0
        skipped = 0
        unknown_user = 0
        inserted = 0
        for row_str in rows:
            if len(row_str) == 0:
                continue

            try:
                i += 1
                row = row_str.split(',')

                programme = programmes_helper.programmes[row[0]]
                ranking_number = int(row[1])
                offer_date_arr = row[2].split('/')
                offer_date = offer_date_util.parse_offer_date(offer_date_arr[0], offer_date_arr[1])
                is_private = row[3].lower() == 'true'
                discord_tag = row[4].split('#') if len(row[4]) > 0 else None

                # If the ranking number is below the programme limit and discord_tag is null, do not import it
                if ranking_number <= programme.places and discord_tag is None:
                    skipped += 1
                    continue

                discord_id = None

                # If discord_tag is not null, try to find the user id using the Discord API
                if discord_tag is not None:
                    user = get(all_members, name=discord_tag[0], discriminator=discord_tag[1])

                    if user:
                        discord_id = str(user.id)
                        await users.add_user(discord_id, user.name)
                    else:
                        print("Can't find user " + row[4])
                        unknown_user += 1
                        if ranking_number <= programme.places:
                            skipped += 1
                            continue

                try:
                    await ranks.add_rank(ranking_number, programme.id, discord_id,
                                         offer_date if ranking_number > programme.places else None,
                                         source)
                except EntryAlreadyExistsError:
                    skipped += 1
                    continue

                if is_private:
                    await ranks.set_is_private_programme(discord_id, True, programme.id)

                inserted += 1

            except Exception as inner:
                raise RuntimeError(f'An exception occurred while processing row {i}') from inner

        return inserted, skipped, unknown_user
