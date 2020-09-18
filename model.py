class Position:
    def __init__(self, timestamp = None, latitude = None, longitude = None, speed = None, processed = False, sent = False) -> None:
        self.timestamp = timestamp
        self.latitude = latitude
        self.longitude = longitude
        self.speed = speed


class Track:
    def __init__(self, id, name, start_line_a, start_line_b):
        self.id = id
        self.name = name
        self.start_line_a = start_line_a
        self.start_line_b = start_line_b