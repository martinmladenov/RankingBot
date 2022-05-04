import discord.ext.commands
from discord_slash.utils.manage_components import create_button, create_actionrow, create_select, create_select_option
from discord_slash.model import ButtonStyle
from services import dm_service
from asyncio import Lock
import time

#TODO: emoji
programme_roles_dict = {
    'cse': 'Computer Science and Engineering',
    'ae': 'Aerospace Engineering',
    'mech': 'Mechanical Engineering',
    'ee': 'Electrical Engineering',
    'nb': 'Nanobiology',
    'aes': 'Applied Earth Science',
    'ap': 'Applied Physics',
    'a': 'Architecture',
    'che': 'Chemical Engineering',
    'idp': 'IDP',
    'lst': 'Life Science & Technology',
    'mst': 'Molecular Science & Technology',
    'm': 'Mathematics',
    'tpm': 'TPM (wannabe engineers)',
    #'ce': 'Civil Engineering'
}

programme_roles_tud = ['cse', 'ae', 'mech', 'ee', 'nb', 'aes', 'ap', 'a', 'lst', 'mst', 'm', 'tpm']
programme_roles_tue = ['cse', 'mech', 'ee', 'ap', 'a', 'che', 'm']
programme_roles_utwente = ['cse', 'mech', 'ee', 'ap', 'che', 'm']

programme_roles = set(programme_roles_dict.values())
programme_roles_all = programme_roles.union({
    'Graduates',
})

student_roles_dict = {
    'tud': 'TU Delft Students',
    'tue': 'TU Eindhoven Students',
    'utwente': 'UTwente Students',
}

student_roles = set(student_roles_dict.values())

applicant_roles_dict = {
    'tud': 'TU Delft Applicants',
    'tue': 'TU Eindhoven Applicants',
    'utwente': 'UTwente Applicants',
}

applicant_roles = set(applicant_roles_dict.values())

accepted_roles_dict = {
    'tud': 'Accepted TU Delft',
    'tue': 'Accepted TU Eindhoven',
    'utwente': 'Accepted UTwente',
}

accepted_roles = set(accepted_roles_dict.values())

last_notification_dict_lock = Lock()
last_notification = dict()


async def should_be_notified(member: discord.Member) -> bool:
    user_id = str(member.id)
    user_roles = set(member.roles)
    async with last_notification_dict_lock:
        if not any(r.name in programme_roles_all for r in user_roles):
            # user has no roles
            curr_time = int(time.time())  # keeps track of time in seconds
            if user_id not in last_notification or \
                    curr_time - last_notification[user_id] >= 60 * 60:  # 1 hour
                last_notification[user_id] = curr_time
                return True
    return False


def process_role_assignment_student(programme: str, uni: str, user_roles: set, guild_roles: list,
                                    to_add: list, to_remove: list):
    # Remove all other programme roles, remove all other student roles,
    # remove all applicant and accepted roles,
    # add correct student and programme roles (if necessary)

    programme_role_name = programme_roles_dict[programme]
    student_role_name = student_roles_dict[uni]
    for role in user_roles:
        role_name = role.name
        if role_name in accepted_roles or role_name in applicant_roles or \
                role_name in programme_roles and role_name != programme_role_name or \
                role_name in student_roles and role_name != student_role_name:
            to_remove.append(role)

    if not any(student_role_name == r.name for r in user_roles):
        to_add.append(next(r for r in guild_roles if r.name == student_role_name))
    if not any(programme_role_name == r.name for r in user_roles):
        to_add.append(next(r for r in guild_roles if r.name == programme_role_name))


async def process_role_assignment_accepted(programme: str, uni: str, user_roles: set, guild_roles: list,
                                           to_add: list, to_remove: list,
                                           bot: discord.ext.commands.Bot, user: discord.User):
    # Remove corresponding applicant role,
    # add correct student and programme roles (if necessary)
    # Send DMs if programme is numerus fixus

    programme_role_name = programme_roles_dict[programme]
    student_role_name = applicant_roles_dict[uni]
    applicant_role_name = applicant_roles_dict[uni]
    accepted_role_name = accepted_roles_dict[uni]
    for role in user_roles:
        role_name = role.name
        if role_name == applicant_role_name or role_name == student_role_name:
            to_remove.append(role)

    if not any(accepted_role_name == r.name for r in user_roles):
        to_add.append(next(r for r in guild_roles if r.name == accepted_role_name))
    if not any(programme_role_name == r.name for r in user_roles):
        to_add.append(next(r for r in guild_roles if r.name == programme_role_name))

    async with (await bot.get_db_conn()).acquire() as connection:
        dm = dm_service.DMService(connection)
        await dm.handle_assignment(user, f"{uni}-{programme}")


def process_role_assignment_applicant(programme: str, uni: str, user_roles: set, guild_roles: list,
                                      to_add: list, to_remove: list):
    # Remove corresponding student and accepted roles,
    # add student and programme roles (if necessary)

    programme_role_name = programme_roles_dict[programme]
    applicant_role_name = applicant_roles_dict[uni]
    accepted_role_name = accepted_roles_dict[uni]
    student_role_name = student_roles_dict[uni]
    for role in user_roles:
        role_name = role.name
        if role_name == student_role_name or role_name == accepted_role_name:
            to_remove.append(role)

    if not any(applicant_role_name == r.name for r in user_roles):
        to_add.append(next(r for r in guild_roles if r.name == applicant_role_name))
    if not any(programme_role_name == r.name for r in user_roles):
        to_add.append(next(r for r in guild_roles if r.name == programme_role_name))


def process_role_removal_all(user_roles: set, to_remove: list):
    # Remove all roles
    for role in user_roles:
        role_name = role.name
        if role_name in accepted_roles or role_name in applicant_roles or \
                role_name in programme_roles or role_name in student_roles:
            to_remove.append(role)


def generate_components(suffix: str, emojis: dict) -> list:
    prefix = 'role_'
    components = [
        # create_actionrow(
        #     create_button(style=ButtonStyle.gray, label='='*15+' '+menu_type.upper()+' '+'='*15, disabled=True),
        # )""",

        create_actionrow(
            #create_button(style=ButtonStyle.green, label="TU Delft:",
            #              emoji=emojis['tud'], disabled=True),
            create_select(
                custom_id='roleselect-tud',
                options = [create_select_option(programme_roles_dict[key], value=prefix + 'tud-' + key + suffix)
                    for key in programme_roles_tud],
                placeholder="Choose your programme",
                min_values=0,
                max_values=len(programme_roles_tud),
            )
        ),
        create_actionrow(
            #create_button(style=ButtonStyle.green, label="TU Eindhoven:",
            #              emoji=emojis['tue'], disabled=True),
            create_select(
                custom_id='roleselect-tue',
                options = [create_select_option(programme_roles_dict[key], value=prefix + 'tue-' + key + suffix)
                    for key in programme_roles_tue],
                placeholder="Choose your programme",
                min_values=0,
                max_values=len(programme_roles_tue),
            )
        ),
        create_actionrow(
            #create_button(style=ButtonStyle.green, label="UTwente",
            #              emoji=emojis['utwente'], disabled=True),
            create_select(custom_id='roleselect-utwente',
                options = [create_select_option(programme_roles_dict[key], value=prefix + 'utwente-' + key + suffix)
                    for key in programme_roles_utwente],
                placeholder="Choose your programme",
                min_values=0,
                max_values=len(programme_roles_utwente),
            )
        ),
    ] #possibly could be even more generified but no

    return components


def generate_components_remove_roles() -> list:
    prefix = 'role_'
    components = [
        create_actionrow(
            create_button(style=ButtonStyle.gray, label="Did you get the wrong roles?", disabled=True),
            create_button(style=ButtonStyle.gray, label="Remove roles",
                          custom_id=prefix + 'remove-remove-remove'),
        ),
    ]

    return components
