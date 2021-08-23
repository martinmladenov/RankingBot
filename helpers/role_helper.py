from discord_slash.utils.manage_components import create_button, create_actionrow
from discord_slash.model import ButtonStyle


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
