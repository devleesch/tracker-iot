import datetime
import json


class Message:
    def __init__(self, device_id, message: str):
        self.device_id = device_id
        self.message = message

    def to_json(self):
        return json.dumps(self.__dict__)
