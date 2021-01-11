import configparser
from threading import Thread

import database
import model
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
            for message in database.QueueService.select_all(self.database_connection):
                message.device_id = self.config['device']['id']
                self.iotcore.publish(message)
                database.PositionService.delete(self.database_connection, message)
