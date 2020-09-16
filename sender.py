from threading import Thread
import time
import paho.mqtt.client as mqttc

import iotcore
import database

class Sender(Thread):
    def __init__(self, iotcore: iotcore.IotCore):
        Thread.__init__(self, name="sender", daemon=True)
        self.iotcore = iotcore
        
        self.database_connection = None

    def run(self):
        self.database_connection = database.Database.connect()
        #self.iotcore.connect()
        while True:
            for p in database.PositionService.select_all_not_sent(self.database_connection):
                print("sending {}".format(p))
                time.sleep(0.5)
                database.PositionService.update_sent_by_timestamp(self.database_connection, p.timestamp)
                #self.iotcore.publish(msg)
            time.sleep(10)
