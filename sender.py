from threading import Thread
import time
import paho.mqtt.client as mqttc
import configparser

import iotcore
import database


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
            for p in database.PositionService.select_all_not_sent(self.database_connection):
                msg = iotcore.Message(
                    self.config['device']['id'],
                    p.timestamp,
                    p.latitude,
                    p.longitude,
                    p.speed
                )
                self.iotcore.publish(msg)
                database.PositionService.update_sent_by_timestamp(self.database_connection, p.timestamp)