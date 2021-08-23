from discord_slash.utils.manage_components import create_button, create_actionrow
from discord_slash.model import ButtonStyle

programme_roles_dict = {
    'cse': 'Computer Science and Engineering',
    'ae': 'Aerospace Engineering',
    'mech': 'Mechanical Engineering',
    'ee': 'Electrical Engineering',
    'nb': 'Nanobiology',
}

programme_roles = set(programme_roles_dict.values())

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


def process_role_assignment_applicant(programme: str, uni: str, user_roles: set, guild_roles: list,
                                      to_add: list, to_remove: list):
    # Remove corresponding student and accepted roles,
    # add  student and programme roles (if necessary)

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


def generate_components(suffix: str, emojis: dict) -> list:
    prefix = 'role_'
    components = [
        # create_actionrow(
        #     create_button(style=ButtonStyle.gray, label='='*15+' '+menu_type.upper()+' '+'='*15, disabled=True),
        # ),
        create_actionrow(
            create_button(style=ButtonStyle.green, label="Computer Science and Engineering:",
                          emoji='\U0001f4bb', disabled=True),  # laptop
            create_button(style=ButtonStyle.blue, label="TU Delft", emoji=emojis['tud'],
                          custom_id=prefix + 'tud-cse' + suffix),
            create_button(style=ButtonStyle.red, label="TU Eindhoven", emoji=emojis['tue'],
                          custom_id=prefix + 'tue-cse' + suffix),
            create_button(style=ButtonStyle.gray, label="UTwente", emoji=emojis['utwente'],
                          custom_id=prefix + 'utwente-cse' + suffix),
        ),
        create_actionrow(
            create_button(style=ButtonStyle.green, label="Aerospace Engineering:",
                          emoji='\U0001f680', disabled=True),  # rocket
            create_button(style=ButtonStyle.blue, label="TU Delft", emoji=emojis['tud'],
                          custom_id=prefix + 'tud-ae' + suffix),
        ),
        create_actionrow(
            create_button(style=ButtonStyle.green, label="Mechanical Engineering:",
                          emoji='\U0001f527', disabled=True),  # wrench
            create_button(style=ButtonStyle.blue, label="TU Delft", emoji=emojis['tud'],
                          custom_id=prefix + 'tud-mech' + suffix),
            create_button(style=ButtonStyle.red, label="TU Eindhoven", emoji=emojis['tue'],
                          custom_id=prefix + 'tue-mech' + suffix),
            create_button(style=ButtonStyle.gray, label="UTwente", emoji=emojis['utwente'],
                          custom_id=prefix + 'utwente-mech' + suffix),
        ),
        create_actionrow(
            create_button(style=ButtonStyle.green, label="Electrical Engineering:",
                          emoji='\U0001f39b', disabled=True),  # control knobs
            create_button(style=ButtonStyle.blue, label="TU Delft", emoji=emojis['tud'],
                          custom_id=prefix + 'tud-ee' + suffix),
            create_button(style=ButtonStyle.red, label="TU Eindhoven", emoji=emojis['tue'],
                          custom_id=prefix + 'tue-ee' + suffix),
            create_button(style=ButtonStyle.gray, label="UTwente", emoji=emojis['utwente'],
                          custom_id=prefix + 'utwente-ee' + suffix),
        ),
        create_actionrow(
            create_button(style=ButtonStyle.green, label="Nanobiology:",
                          emoji='\U0001f9ec', disabled=True),  # dna
            create_button(style=ButtonStyle.blue, label="TU Delft", emoji=emojis['tud'],
                          custom_id=prefix + 'tud-nb' + suffix),
        ),
    ]

    return components
