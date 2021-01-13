from threading import Thread

import database
import iotcore


class Sender(Thread):
    def __init__(self, iotcore: iotcore.IotCore):
        Thread.__init__(self, name="sender", daemon=True)
        self.iotcore = iotcore
        self.database_connection = None

    def run(self):
        self.database_connection = database.Database.connect()
        self.iotcore.connect()
        while True:
            for message in database.QueueService.select_all(self.database_connection):
                self.iotcore.publish(message.value)
                database.QueueService.delete(self.database_connection, message)
