import discord
from enum import IntEnum, Enum
from utils import offer_date_util
from helpers import programmes_helper
from datetime import datetime, date
import re
import constants
from asyncio import Lock

user_locks = dict()
user_lock_dict_lock = Lock()


class DMService:
    def __init__(self, db_conn):
        self.db_conn = db_conn

    async def handle_incoming_dm(self, message: discord.Message) -> bool:
        user_id = str(message.author.id)

        dm_row = await self.db_conn.fetchrow('SELECT id, programme FROM dms '
                                             'WHERE user_id = $1 AND status = $2',
                                             user_id, self.DmStatus.SENT)
        if not dm_row:
            return False

        dm_row_id, programme_id = dm_row

        if message.content.lower() in ['wrong', 'stop']:
            await self.db_conn.execute('UPDATE dms SET status = $1, done = $2 '
                                       'WHERE id = $3', self.DmStatus.REFUSED, datetime.utcnow(), dm_row_id)
            await message.channel.send('Noted. Sorry for bothering you!')
            await self.process_next_scheduled_dm(message.author)
            return True

        result = await self.handle_rank_response(message, programme_id)

        if result:
            await self.db_conn.execute('UPDATE dms SET status = $1, done = $2 '
                                       'WHERE id = $3', self.DmStatus.DONE, datetime.utcnow(), dm_row_id)
            await self.process_next_scheduled_dm(message.author)

        return result

    async def handle_rank_response(self, message: discord.Message, dm_programme: str) -> bool:
        try:
            match = re.search(r'^[^A-Za-z0-9]*(\d+)[^A-Za-z0-9]+(\d+)[^A-Za-z0-9]+([A-Za-z0-9]+)[^A-Za-z0-9]*$',
                              message.content)

            if match is None:
                raise ValueError

            parsed_rank = int(match.group(1))
            parsed_date = offer_date_util.parse_offer_date(match.group(2), match.group(3))

            if parsed_rank <= 0 or parsed_rank >= 10000:
                await message.channel.send('Sorry, something seems wrong with the data you provided. '
                                           'Please check your ranking number and date. '
                                           'Use the format `<rank> <day> <month>`.\n'
                                           '_For example, if your ranking number is 100 and you\'ve received '
                                           'an offer on 15 April, type `100 15 April`._')
                return False

            if parsed_rank <= programmes_helper.programmes[dm_programme].places[constants.current_year] \
                    and parsed_date != date(constants.current_year, 4, 15):
                await message.channel.send('Sorry, the ranking number you provided is within the programme limit '
                                           'but the offer date is different from 15 April, when everyone with such '
                                           'ranking numbers received their offers. Please check your ranking '
                                           'number and date and try again.')
                return False

            rank = await self.db_conn.fetchval('SELECT rank FROM ranks '
                                               'WHERE user_id = $1 AND programme = $2 AND year = $3',
                                               str(message.author.id), dm_programme, constants.current_year)

            if rank:
                if rank != parsed_rank:
                    await message.channel.send(f'It seems that you\'ve already set your ranking number '
                                               f'to **{rank}**. '
                                               f'If that\'s incorrect, please use '
                                               f'`/clearrank` to clear it '
                                               f'and reply with `{message.content}` again.')
                    return False

                await self.db_conn.execute('UPDATE ranks SET offer_date = $1 '
                                           'WHERE user_id = $2 AND programme = $3 AND year = $4',
                                           parsed_date, str(message.author.id), dm_programme, constants.current_year)
            else:
                await self.db_conn.execute(
                    'INSERT INTO ranks (user_id, rank, programme, offer_date, is_private, source, year) '
                    'VALUES ($1, $2, $3, $4, $5, $6, $7)',
                    str(message.author.id), parsed_rank, dm_programme, parsed_date, True, 'dm', constants.current_year)

            await message.channel.send('**Thank you for the information!**\n'
                                       'We will do our best to put it to good use and help other applicants '
                                       'determine when they might receive an offer.\n'
                                       '_Note: Your ranking number is now protected, so it is hidden from the '
                                       'statistics visible to server members. If you want it to be displayed, '
                                       'you can use `/toggleprivaterank`._')

            return True
        except ValueError:
            await message.channel.send('Sorry, couldn\'t parse your response. Please use the following format: '
                                       '`<rank> <day> <month>`.\n_For example, if your ranking number is '
                                       '100 and you\'ve received an offer on 15 April, type `100 15 April`._')
        except:
            await message.channel.send('Sorry, an unexpected error occurred while processing your response.')
            raise

        return False

    async def process_next_scheduled_dm(self, member: discord.Member):
        user_id = str(member.id)

        dm_row = await self.db_conn.fetchrow('SELECT id, programme FROM dms '
                                             'WHERE user_id = $1 AND status = $2',
                                             user_id, self.DmStatus.SCHEDULED)
        if not dm_row:
            return

        dm_row_id, programme_id = dm_row

        programme = programmes_helper.programmes[programme_id]

        result = await self.send_scheduled_dm(member, programme)

        if not result:
            return

        await self.db_conn.execute('UPDATE dms SET status = $1, sent = $2 '
                                   'WHERE id = $3', self.DmStatus.SENT, datetime.utcnow(), dm_row_id)

    class DmStatus(IntEnum):
        SCHEDULED = 0,
        SENT = 1,
        DONE = 2,
        REFUSED = 3

    class University(Enum):
        TUD = 0,
        TUE = 1

    async def get_member_programmes(self, member: discord.Member, uni: University) -> list:
        cse_role = 'Computer Science and Engineering'
        ae_role = 'Aerospace Engineering'
        nb_role = 'Nanobiology'

        roles = list(map(lambda x: x.name, member.roles))

        if any(map(lambda x: 'students' in x.lower() and x != 'IB Students', roles)):
            return list()

        if uni == self.University.TUD:
            programmes = list()
            if ae_role in roles:
                programmes.append('tud-ae')
            if cse_role in roles:
                programmes.append('tud-cse')
            if nb_role in roles:
                programmes.append('tud-nb')
            return programmes
        if uni == self.University.TUE:
            if cse_role in roles:
                return ['tue-cse']

        return list()

    async def handle_reaction(self, member: discord.Member, emoji: str):
        if emoji == 'TUD':
            uni = self.University.TUD
        elif emoji == 'TuE':
            uni = self.University.TUE
        else:
            return

        programmes = await self.get_member_programmes(member, uni)

        if not programmes:
            return

        user_id = str(member.id)

        # Find or create and acquire user lock
        async with user_lock_dict_lock:
            if user_id not in user_locks:
                user_locks[user_id] = Lock()

            lock = user_locks[user_id]

        async with lock:
            user_data_row = await self.db_conn.fetchrow('SELECT user_id FROM user_data '
                                                        'WHERE user_id = $1',
                                                        user_id)
            if not user_data_row:
                await self.db_conn.execute('INSERT INTO user_data (user_id, username) '
                                           'VALUES ($1, $2)',
                                           user_id, member.name)

            sent_programmes = await self.db_conn.fetch('SELECT programme FROM dms '
                                                       'WHERE user_id = $1 AND status IN ($2, $3)',
                                                       user_id, self.DmStatus.SENT, self.DmStatus.SCHEDULED)

            should_send = len(sent_programmes) == 0
            for programme in programmes:
                if any(programme == p[0] for p in sent_programmes):
                    continue

                rank_row = await self.db_conn.fetchrow(
                    'SELECT rank FROM ranks '
                    'WHERE user_id = $1 AND programme = $2 '
                    'AND offer_date IS NOT NULL AND year = $3',
                    user_id, programme, constants.current_year)

                if rank_row is not None:
                    continue
                sched_time = datetime.utcnow()
                sent = False
                if should_send:
                    sent = await self.send_first_dm(member, programmes_helper.programmes[programme])
                    should_send = False

                await self.db_conn.execute('INSERT INTO dms (user_id, programme, status, scheduled, sent) '
                                           'VALUES ($1, $2, $3, $4, $5)',
                                           user_id, programme,
                                           self.DmStatus.SENT if sent else self.DmStatus.SCHEDULED,
                                           sched_time,
                                           datetime.utcnow() if sent else None)

        # Delete user lock
        async with user_lock_dict_lock:
            if not lock.locked() and user_id in user_locks:
                del user_locks[user_id]

    async def send_first_dm(self, member: discord.Member, programme: programmes_helper.Programme) -> bool:
        message = '**Hi {0}!**\n' \
                  'On the **Dutch 3TU Applicants** server, you chose a role indicating that you have been ' \
                  'accepted to the **{1}** programme at {2} **{3}**. Congratulations!\n' \
                  'We\'d appreciate it a lot if you\'d like to help other applicants estimate when they might ' \
                  'receive an offer by providing us with your **ranking number** and **the date you received ' \
                  'your offer on Studielink**. If you want to help, please reply to this ' \
                  'message in the following format: `<rank> <day> <month>`.\n' \
                  '_For example, if your ranking number is 100 and you received an offer on 15 April, ' \
                  'please reply `100 15 April`._\n' \
                  '**Thanks for your help!**\n' \
                  '_Note: If you don\'t want to share your ranking number or the date, feel free to round them ' \
                  'up or down. Additionally, if you provide any information here, it will always be anonymized ' \
                  'before other people can see it. If you wish, you can make it public later._\n' \
                  'If you haven\'t applied for the **{1}** programme at **{3}** but have the server role ' \
                  'for a different reason, please type `wrong`.\n' \
                  'If you don\'t want to share your ranking number, please type `stop`.' \
            .format(member.name, programme.display_name, programme.icon, programme.uni_name)

        try:
            dm_channel = await member.create_dm()
            await dm_channel.send(message)
            return True
        except Exception as e:
            print(f'failed to send message to {member.name}: {str(e)}')
            return False

    async def send_scheduled_dm(self, member: discord.Member, programme: programmes_helper.Programme) -> bool:
        message = 'You also have a role indicating that you\'ve been accepted to ' \
                  '**{0}** at {1} **{2}**.\n' \
                  'Would you like to share your _ranking number_ and _the date you received ' \
                  'your offer_ for this programme? If so, please reply in the following format: ' \
                  '`<rank> <day> <month>`.\n' \
                  '_For example, if your ranking number is 100 and you received an offer on 15 April, ' \
                  'please reply `100 15 April`._\n' \
                  '**Thanks again!**\n' \
                  'Like before, you can type `wrong` if you haven\'t applied to this programme, or `stop` if you' \
                  'don\'t want to share your ranking number.' \
            .format(programme.display_name, programme.icon, programme.uni_name)

        try:
            dm_channel = await member.create_dm()
            await dm_channel.send(message)
            return True
        except Exception as e:
            print(f'failed to send message to {member.name}: {str(e)}')
            return False
