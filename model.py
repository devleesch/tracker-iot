import json


class Message:
    def __init__(self, uuid, value, trip) -> None:
        self.uuid = uuid
        self.value = value
        self.trip = trip

    def to_json(self):
        return json.dumps(self.__dict__)


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

TRACKS = [
    Track(1, "Mettet", Position(latitude=50.300936, longitude=4.649522), Position(latitude=50.300821, longitude=4.649592)),
    Track(2, "Chambley", Position(latitude=49.026944, longitude=5.892370), Position(latitude=49.026839, longitude=5.892347))
]