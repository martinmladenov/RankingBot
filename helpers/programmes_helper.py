from discord_slash.utils.manage_commands import create_choice


class Programme:
    def __init__(self, programme_id: str, display_name: str, uni_name: str, icon: str, places: dict, visa_cutoff,
                 graph_colour: str):
        self.id = programme_id
        self.display_name = display_name
        self.uni_name = uni_name
        self.icon = icon
        self.places = places
        self.visa_cutoff = visa_cutoff
        self.graph_colour = graph_colour


programmes = {
    'tud-cse': Programme(
        'tud-cse',
        'Computer Science and Engineering',
        'TU Delft',
        '<:TUD:555817896203255824>',
        {2020: 500, 2021: 500, 2022: 500},
        (15, 6),
        '#1f77b4'
    ),
    'tud-ae': Programme(
        'tud-ae',
        'Aerospace Engineering',
        'TU Delft',
        '<:TUD:555817896203255824>',
        {2020: 440, 2021: 440, 2022: 440},
        (15, 6),
        '#c9792f'
    ),
    'tue-cse': Programme(
        'tue-cse',
        'Computer Science and Engineering',
        'TU Eindhoven',
        '<:TuE:562730919815807003>',
        {2020: 325, 2021: 325, 2022: 325},
        None,
        '#bb3e2e'
    ),
    'ut-tcs': Programme(
        'ut-tcs',
        'Technical Computer Science',
        'UTwente',
        '<:UTWENTE:555817816918327296>',
        {2022: 400},
        (1, 6),
        '#b03c56'
    ),
    'tue-me': Programme(
        'tue-me',
        'Mechanical Engineering',
        'TU Eindhoven',
        '<:TuE:562730919815807003>',
        {2022: 360},
        None,
        '#c9792f'
    ),
    'tud-nb': Programme(
        'tud-nb',
        'Nanobiology',
        'TU Delft',
        '<:TUD:555817896203255824>',
        {2020: 100, 2021: 120, 2022: 120},
        (15, 6),
        '#b03c56'
    ),
}


def get_ids_string():
    return "/".join(programmes.keys())


def get_programme_choices():
    return list(
        create_choice(
            name=f'{programmes[programme_id].uni_name} {programmes[programme_id].display_name}',
            value=programme_id
        ) for programme_id in programmes
    )


def get_year_choices():
    return list(create_choice(name=str(year), value=year) for year in [2022, 2021, 2020])
