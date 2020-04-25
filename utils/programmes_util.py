class Programme:
    def __init__(self, programme_id: str, display_name: str, places: int):
        self.id = programme_id
        self.display_name = display_name
        self.places = places


programmes = {
    'tud-cse': Programme('tud-cse', 'TU Delft Computer Science and Engineering', 500),
    'tud-ae': Programme('tud-ae', 'TU Delft Aerospace Engineering', 440),
    'tue-cse': Programme('tue-cse', 'TU Eindhoven Computer Science and Engineering', 325),
}


def get_ids_string():
    return "/".join(programmes.keys())
