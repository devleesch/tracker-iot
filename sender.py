import configparser
from threading import Thread

import database
import iotcore


class Sender(Thread):
    def __init__(self, config: configparser.ConfigParser, iotcore: iotcore.IotCore):
        Thread.__init__(self, name="sender", daemon=True)
        self.config = config
        self.iotcore = iotcore
        
        self.database_connection = None

    def run(self):
        self.database_connection = database.Database.connect()
        self.iotcore.connect()
        while True:
            for p in database.PositionService.select_all(self.database_connection):
                msg = iotcore.Message(
                    self.config['device']['id'],
                    p.timestamp,
                    p.latitude,
                    p.longitude,
                    p.speed
                )
                self.iotcore.publish(msg)
                database.PositionService.delete(self.database_connection, p)
