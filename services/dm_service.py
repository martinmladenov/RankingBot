import discord
from enum import IntEnum, Enum
from utils import offer_date_util
from helpers import programmes_helper
from datetime import datetime, date
import re
import constants


class DMService:
    def __init__(self, db_conn):
        self.db_conn = db_conn

    async def send_programme_rank_dm(self, member: discord.Member, programme: programmes_helper.Programme,
                                     send_messages: bool,
                                     results):
        programme_id = programme.id
        user_id = member.id

        rank_row = await self.db_conn.fetchrow(
            'SELECT rank FROM ranks WHERE user_id = $1 AND programme = $2 AND offer_date IS NOT NULL AND year = $3',
            str(user_id), programme_id, constants.current_year)

        if rank_row:
            results['rank-already-set'].append(member)
            return False

        user_data_row = await self.db_conn.fetchrow('SELECT user_id, dm_status FROM user_data WHERE user_id = $1',
                                                    str(user_id))

        if user_data_row and user_data_row[1] is not None:
            results['dm-status-not-null'].append(member)
            return False

        if not send_messages:
            return True

        message = '**Hi {0}!**\n' \
                  'On the **3TU** server, you have chosen a role indicating you have been accepted to the ' \
                  '**{1}** programme at {2} **{3}**. Congratulations!\n' \
                  'We\'d appreciate it a lot if you\'d like to help other applicants determine when they might ' \
                  'receive an offer by providing us with your **ranking number** and **the date you\'ve received ' \
                  'your offer on Studielink**. If you want to participate in this research, please reply to this ' \
                  'message in the following format: `<rank> <day> <month>`.\n' \
                  '_For example, if your ranking number is 100 and you\'ve received an offer on 15 April, ' \
                  'please reply `100 15 April`._\n' \
                  '**Thanks for your help!**\n' \
                  '_Note: If you don\'t want to share your ranking number or the date, feel free to round them ' \
                  'up or down. Additionally, if you provide any information here, your username won\'t be shown ' \
                  'alongside it on the statistics visible to all server members. If you want it to be displayed, ' \
                  'you can type `.toggleprivaterank` on any channel on the server._\n' \
                  'If you haven\'t applied for the **{1}** programme at **{3}** but have the server role ' \
                  'for a different reason, please type `wrong`.' \
            .format(member.name, programme.display_name, programme.icon, programme.uni_name)

        try:
            dm_channel = await member.create_dm()
            await dm_channel.send(message)
        except Exception as e:
            print(f'failed to send message to {member.name}: {str(e)}')
            results['cannot-send-dm'].append(member)
            return False

        if not user_data_row:
            await self.db_conn.execute('INSERT INTO user_data (user_id, username, dm_programme, dm_status, '
                                       'dm_last_sent) '
                                       'VALUES ($1, $2, $3, $4, $5)',
                                       str(user_id), member.name, programme_id, self.DmStatus.AWAITING_RANK,
                                       datetime.utcnow())
        else:
            await self.db_conn.execute(
                'UPDATE user_data SET dm_programme = $1, dm_status = $2, dm_last_sent = $3 WHERE user_id = $4',
                programme_id, self.DmStatus.AWAITING_RANK, datetime.utcnow(), str(user_id))

        return True

    async def get_users_with_active_dm_sent_before_date(self, max_datetime: datetime):
        users = await self.db_conn.fetch('SELECT user_id, dm_programme, username FROM user_data '
                                         'WHERE dm_status = $1 '
                                         'AND dm_last_sent <= $2',
                                         self.DmStatus.AWAITING_RANK, max_datetime)
        return users

    async def send_programme_rank_reminder_dm(self, user: discord.User, programme: programmes_helper.Programme):
        user_id = user.id

        message = '**Hello {0}!**\n' \
                  'We\'d be very grateful if you could provide us with your **ranking number** and ' \
                  '**the date you\'ve received your offer on Studielink** for the **{1}** programme at {2} **{3}**. ' \
                  'This information is very helpful to other applicants who have not received an offer yet.\n' \
                  'If you want to help, please reply to this message in the following format: `<rank> <day> ' \
                  '<month>`.\n' \
                  '_For example, if your ranking number is 100 and you\'ve received an offer on 15 April, ' \
                  'please reply `100 15 April`._\n' \
                  '**Thanks a lot!**\n' \
                  'If you haven\'t applied for the **{1}** programme at **{3}**, please type `wrong`.\n' \
                  'If you don\'t want to receive any more messages from the bot, type `stop`.' \
            .format(user.name, programme.display_name, programme.icon, programme.uni_name)

        try:
            dm_channel = await user.create_dm()
            await dm_channel.send(message)
        except Exception as e:
            print(f'failed to send message to {user.name}: {str(e)}')
            return False

        await self.db_conn.execute('UPDATE user_data SET dm_last_sent = $1 WHERE user_id = $2',
                                   datetime.utcnow(), str(user_id))

        return True

    async def handle_awaiting_rank(self, message: discord.Message, dm_programme: str):
        try:
            if message.content.lower() in ['wrong', 'stop']:
                await self.db_conn.execute('INSERT INTO excluded_programmes (user_id, programme) VALUES ($1, $2)',
                                           str(message.author.id), dm_programme)
                await self.db_conn.execute('UPDATE user_data SET dm_programme = NULL, dm_status = NULL '
                                           'WHERE user_id = $1', str(message.author.id))
                await message.channel.send('Noted. Sorry for bothering you!')
                return True

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
                                               f'If that\'s incorrect, please type '
                                               f'`.clearrank {dm_programme} {constants.current_year}` '
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

            await self.db_conn.execute('UPDATE user_data SET dm_programme = NULL, dm_status = NULL '
                                       'WHERE user_id = $1', str(message.author.id))

            await message.channel.send('**Thank you for the information!**\n'
                                       'We will do our best to put it to good use and help other applicants '
                                       'determine when they might receive an offer.\n'
                                       '_Note: Your username is now hidden from the statistics visible to '
                                       'all server members. If you want it to be displayed, '
                                       'you can type `.toggleprivaterank` on any channel on the server._')

            return True
        except ValueError:
            await message.channel.send('Sorry, couldn\'t parse your response. Please use the following format: '
                                       '`<rank> <day> <month>`.\n_For example, if your ranking number is '
                                       '100 and you\'ve received an offer on 15 April, type `100 15 April`._')
        except:
            await message.channel.send('Sorry, an unexpected error occurred while processing your response.')
            raise

        return False

    class DmStatus(IntEnum):
        SCHEDULED = 0
        SENT = 1
        DONE = 2

    class University(Enum):
        TUD = 0,
        TUE = 1

    async def get_member_programmes(self, member: discord.Member, uni: University) -> list:
        cse_role = 'Computer Science and Engineering'
        ae_role = 'Aerospace Engineering'

        roles = list(map(lambda x: x.name, member.roles))

        if any(map(lambda x: 'students' in x.lower() and x != 'IB Students', roles)):
            return list()

        excluded_programmes_rows = await self.db_conn.fetch(
            'SELECT programme FROM excluded_programmes WHERE user_id = $1',
            str(member.id))
        excluded_programmes = list(map(lambda x: x[0], excluded_programmes_rows))

        if uni == self.University.TUD:
            programmes = list()
            if ae_role in roles and 'tud-ae' not in excluded_programmes:
                programmes.append('tud-ae')
            if cse_role in roles and 'tud-cse' not in excluded_programmes:
                programmes.append('tud-cse')
            return programmes
        if uni == self.University.TUE:
            if cse_role in roles and 'tue-cse' not in excluded_programmes:
                return ['tue-cse']

        return list()



    async def send_first_dm(self, member: discord.Member, programme: programmes_helper.Programme) -> bool:
        message = '**Hi {0}!**\n' \
                  'On the **3TU** server, your roles indicate that you have been accepted to the ' \
                  '**{1}** programme at {2} **{3}**. Congratulations!\n' \
                  'We\'d appreciate it a lot if you\'d like to help other applicants determine when they might ' \
                  'receive an offer by providing us with your **ranking number** and **the date you\'ve received ' \
                  'your offer on Studielink**. If you want to help, please reply to this ' \
                  'message in the following format: `<rank> <day> <month>`.\n' \
                  '_For example, if your ranking number is 100 and you received an offer on 15 April, ' \
                  'please reply `100 15 April`._\n' \
                  '**Thanks for your help!**\n' \
                  '_Note: If you don\'t want to share your ranking number or the date, feel free to round them ' \
                  'up or down. Additionally, if you provide any information here, your username will not be shown ' \
                  'alongside it on the statistics visible to all server members. If you want it to be displayed, ' \
                  'you can type `.toggleprivaterank` on any channel on the server._\n' \
                  'If you haven\'t applied for the **{1}** programme at **{3}** but have the server role ' \
                  'for a different reason, please type `wrong`.' \
            .format(member.name, programme.display_name, programme.icon, programme.uni_name)

        try:
            dm_channel = await member.create_dm()
            await dm_channel.send(message)
            return True
        except Exception as e:
            print(f'failed to send message to {member.name}: {str(e)}')
            return False
