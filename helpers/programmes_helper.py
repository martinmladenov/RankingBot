class Programme:
    def __init__(self, programme_id: str, display_name: str, uni_name: str, icon: str, places: int):
        self.id = programme_id
        self.display_name = display_name
        self.uni_name = uni_name
        self.icon = icon
        self.places = places


programmes = {
    'tud-cse': Programme(
        'tud-cse',
        'Computer Science and Engineering',
        'TU Delft',
        '<:TUD:555817896203255824>',
        500
    ),
    'tud-ae': Programme(
        'tud-ae',
        'Aerospace Engineering',
        'TU Delft',
        '<:TUD:555817896203255824>',
        440
    ),
    'tue-cse': Programme(
        'tue-cse',
        'Computer Science and Engineering',
        'TU Eindhoven',
        '<:TuE:562730919815807003>',
        325
    ),
    'tud-nb': Programme(
        'tud-nb',
        'Nanobiology',
        'TU Delft',
        '<:TUD:555817896203255824>',
        100
    ),
}


def get_ids_string():
    return "/".join(programmes.keys())
