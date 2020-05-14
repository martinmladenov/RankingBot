import discord
from enum import IntEnum, Enum
from utils import programmes_util, offer_date_util
from database import db_fetchall, db_exec
from datetime import datetime, date
import re


async def send_programme_rank_dm(member: discord.Member, programme: programmes_util.Programme, send_messages: bool,
                                 results):
    programme_id = programme.id
    user_id = member.id

    rank_row = db_fetchall('SELECT rank FROM ranks WHERE user_id = %s AND programme = %s', (str(user_id), programme_id))

    if rank_row:
        results['rank-already-set'].append(member)
        return False

    user_data_row = db_fetchall('SELECT user_id, dm_status FROM user_data WHERE user_id = %s', (str(user_id),))

    if user_data_row and user_data_row[0][1] is not None:
        results['dm-status-not-null'].append(member)
        return False

    if not send_messages:
        return True

    message = '**Hi {0}!**\n' \
              'On the **3TU** server, you have chosen a role indicating you have been accepted to the ' \
              '**{1}** programme at {2} **{3}**. Congratulations!\n' \
              'We\'d appreciate it a lot if you\'d like to help other applicants determine when they might receive ' \
              'an offer by providing us with your **ranking number** and **the date you\'ve received your offer ' \
              'on Studielink**. If you want to participate in this research, please reply to this message in the ' \
              'following format: `<rank> <day> <month>`.\n' \
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
        db_exec('INSERT INTO user_data (user_id, username, dm_programme, dm_status, dm_last_sent) '
                'VALUES (%s, %s, %s, %s, %s)',
                (str(user_id), member.name, programme_id, DmStatus.AWAITING_RANK, datetime.utcnow()))
    else:
        db_exec('UPDATE user_data SET dm_programme = %s, dm_status = %s, dm_last_sent = %s WHERE user_id = %s',
                (programme_id, DmStatus.AWAITING_RANK, datetime.utcnow(), str(user_id)))

    return True


async def send_programme_rank_reminder_dm(user: discord.User, programme: programmes_util.Programme):
    user_id = user.id

    message = '**Hello {0}!**\n' \
              'We\'d be very grateful if you could provide us with your **ranking number** and ' \
              '**the date you\'ve received your offer on Studielink** for the **{1}** programme at {2} **{3}**. ' \
              'This information is very helpful to other applicants who have not received an offer yet.\n' \
              'If you want to help, please reply to this message in the following format: `<rank> <day> <month>`.\n' \
              '_For example, if your ranking number is 100 and you\'ve received an offer on 15 April, ' \
              'please reply `100 15 April`._\n' \
              '**Thanks a lot!**\n' \
              'If you haven\'t applied for the **{1}** programme at **{3}**, please type `wrong`.' \
        .format(user.name, programme.display_name, programme.icon, programme.uni_name)

    try:
        dm_channel = await user.create_dm()
        await dm_channel.send(message)
    except Exception as e:
        print(f'failed to send message to {user.name}: {str(e)}')
        return False

    db_exec('UPDATE user_data SET dm_last_sent = %s WHERE user_id = %s',
            (datetime.utcnow(), str(user_id)))

    return True


async def handle_awaiting_rank(message: discord.Message, dm_programme: str):
    try:
        if message.content.lower() == 'wrong':
            db_exec('INSERT INTO excluded_programmes (user_id, programme) VALUES (%s, %s)',
                    (str(message.author.id), dm_programme))
            db_exec('UPDATE user_data SET dm_programme = NULL, dm_status = NULL '
                    'WHERE user_id = %s', (str(message.author.id),))
            await message.channel.send('Noted. Sorry for bothering you!')
            return True

        match = re.search(r'^(\d+)[^A-Za-z0-9]+(\d+)[^A-Za-z0-9]+([A-Za-z0-9]+)$', message.content)

        if match is None:
            raise ValueError

        parsed_rank = int(match.group(1))
        parsed_date = offer_date_util.parse_offer_date(match.group(2), match.group(3))

        if parsed_rank <= 0 or parsed_rank >= 10000:
            await message.channel.send('Sorry, something seems wrong with the data you provided. '
                                       'Please check your ranking number and date. '
                                       'Use the format `<rank> <day> <month>`.\n'
                                       '_For example, if your ranking number is 100 and you\'ve received an offer on '
                                       '15 April, type `100 15 April`._')
            return False

        if parsed_rank <= programmes_util.programmes[dm_programme].places and parsed_date != date(2020, 4, 15):
            await message.channel.send('Sorry, the ranking number you provided is within the programme limit '
                                       'but the offer date is different from 15 April, when everyone with such '
                                       'ranking numbers received their offers. Please check your ranking '
                                       'number and date and try again.')
            return False

        rank_row = db_fetchall('SELECT rank FROM ranks WHERE user_id = %s AND programme = %s',
                               (str(message.author.id), dm_programme))

        if rank_row:
            if rank_row[0][0] != parsed_rank:
                await message.channel.send(f'It seems that you\'ve already set your ranking number '
                                           f'to **{rank_row[0][0]}**. '
                                           f'If that\'s incorrect, please type `.clearrank {dm_programme}`'
                                           f'and reply with `{message.content}` again.')
                return False

            db_exec('UPDATE ranks SET offer_date = %s WHERE user_id = %s AND programme = %s',
                    (parsed_date, str(message.author.id), dm_programme))
        else:
            db_exec('INSERT INTO ranks (user_id, rank, programme, offer_date) VALUES (%s, %s, %s, %s)',
                    (message.author.id, parsed_rank, dm_programme, parsed_date))

        db_exec('UPDATE user_data SET is_private = TRUE, dm_programme = NULL, dm_status = NULL '
                'WHERE user_id = %s', (str(message.author.id),))

        await message.channel.send('**Thank you for the information!**\n'
                                   'We will do our best to put it to good use and help other applicants determine when '
                                   'they might receive an offer.\n'
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

    return False


class DmStatus(IntEnum):
    AWAITING_PROGRAMME = 0
    AWAITING_RANK = 1
    AWAITING_DATE = 2


class University(Enum):
    TUD = 0,
    TUE = 1


def get_member_programme(member: discord.Member, uni: University):
    cse_role = 'Computer Science and Engineering'
    ae_role = 'Aerospace Engineering'

    roles = list(map(lambda x: x.name, member.roles))

    if any(map(lambda x: 'students' in x.lower() and x != 'IB Students', roles)):
        return None

    excluded_programmes_rows = db_fetchall('SELECT programme FROM excluded_programmes WHERE user_id = %s',
                                           (str(member.id),))
    excluded_programmes = list(map(lambda x: x[0], excluded_programmes_rows))

    if uni == University.TUD:
        if ae_role in roles and 'tud-ae' not in excluded_programmes:
            return 'tud-ae'
        if cse_role in roles and 'tud-cse' not in excluded_programmes:
            return 'tud-cse'
    if uni == University.TUE:
        if cse_role in roles and 'tue-cse' not in excluded_programmes:
            return 'tue-cse'

    return None
