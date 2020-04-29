class Programme:
    def __init__(self, programme_id: str, display_name: str, places: int):
        self.id = programme_id
        self.display_name = display_name
        self.places = places


programmes = {
    'tud-cse': Programme('tud-cse', '<:TUD:555817896203255824> TU Delft Computer Science and Engineering', 500),
    'tud-ae': Programme('tud-ae', '<:TUD:555817896203255824> TU Delft Aerospace Engineering', 440),
    'tue-cse': Programme('tue-cse', '<:TuE:562730919815807003> TU Eindhoven Computer Science and Engineering', 325),
}


def get_ids_string():
    return "/".join(programmes.keys())
