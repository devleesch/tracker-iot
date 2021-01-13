from threading import Thread

import database
import iotcore


class Sender(Thread):
    def __init__(self, iotcore: iotcore.IotCore):
        Thread.__init__(self, name="sender", daemon=True)
        self.iotcore = iotcore
        self.database_connection = None
        self.stop = False

    def run(self):
        self.database_connection = database.Database.connect()
        self.iotcore.connect()
        while not self.stop:
            for message in database.QueueService.select_all(self.database_connection):
                self.iotcore.publish(message.value)
                database.QueueService.delete(self.database_connection, message)
        self.iotcore.disconnect()
