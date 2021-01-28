class Programme:
    def __init__(self, programme_id: str, display_name: str, uni_name: str, icon: str, places: int, visa_cutoff):
        self.id = programme_id
        self.display_name = display_name
        self.uni_name = uni_name
        self.icon = icon
        self.places = places
        self.visa_cutoff = visa_cutoff


programmes = {
    'tud-cse': Programme(
        'tud-cse',
        'Computer Science and Engineering',
        'TU Delft',
        '<:TUD:555817896203255824>',
        500,
        (15, 6)
    ),
    'tud-ae': Programme(
        'tud-ae',
        'Aerospace Engineering',
        'TU Delft',
        '<:TUD:555817896203255824>',
        440,
        (15, 6)
    ),
    'tue-cse': Programme(
        'tue-cse',
        'Computer Science and Engineering',
        'TU Eindhoven',
        '<:TuE:562730919815807003>',
        325,
        None
    ),
    'tud-nb': Programme(
        'tud-nb',
        'Nanobiology',
        'TU Delft',
        '<:TUD:555817896203255824>',
        100,
        (15, 6)
    ),
}


def get_ids_string():
    return "/".join(programmes.keys())
