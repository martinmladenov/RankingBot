import discord
from enum import IntEnum
from utils import programmes_util
from database import db_fetchall, db_exec
from datetime import datetime


async def send_programme_rank_dm(member: discord.Member, programme: programmes_util.Programme):
    programme_id = programme.id
    user_id = member.id

    rank_row = db_fetchall('SELECT rank FROM ranks WHERE user_id = %s AND programme = %s', (str(user_id), programme_id))

    if rank_row:
        print(f'skipping {member.name}: rank already set')
        return False

    user_data_row = db_fetchall('SELECT user_id, dm_status FROM user_data WHERE user_id = %s', (str(user_id),))

    if user_data_row and user_data_row[0][1] is not None:
        print(f'skipping {member.name}: dm_status = {user_data_row[0][1]}')
        return False

    message = '**Hi %s!**\n' \
              'On the **3TU** server, you have chosen a role indicating you have been accepted to the ' \
              '**%s** programme at %s **%s**. Congratulations!\n' \
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
              'you can type `.toggleprivaterank` on any channel on the server._' \
              % (member.name, programme.display_name, programme.icon, programme.uni_name)

    try:
        dm_channel = await member.create_dm()
        await dm_channel.send(message)
    except Exception as e:
        print(f'failed to send message to {member.name}: {str(e)}')
        return False

    if not user_data_row:
        db_exec('INSERT INTO user_data (user_id, dm_programme, dm_status, dm_last_sent) VALUES (%s, %s, %s, %s)',
                (str(user_id), programme_id, DmStatus.AWAITING_RANK, datetime.utcnow()))
    else:
        db_exec('UPDATE user_data SET dm_programme = %s, dm_status = %s, dm_last_sent = %s WHERE user_id = %s',
                (programme_id, DmStatus.AWAITING_RANK, datetime.utcnow(), str(user_id)))

    return True


class DmStatus(IntEnum):
    AWAITING_PROGRAMME = 0
    AWAITING_RANK = 1
    AWAITING_DATE = 2
