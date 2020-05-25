import datetime
import json


class Message:
    def __init__(self, device_id, message: str, timestamp: datetime.datetime):
        self.device_id = device_id
        self.message = message
        self.datetime = timestamp

    def to_json(self):
        return json.dumps(self.__dict__, default=Message.json_format)

    @staticmethod
    def json_format(obj):
        if (isinstance(obj, datetime.time)):
            return obj.isoformat()
        elif (isinstance(obj, datetime.datetime)):
            return obj.isoformat()
