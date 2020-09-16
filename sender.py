from threading import Thread
import time
import paho.mqtt.client as mqttc
import configparser
import datetime

import iotcore
import database


class Sender(Thread):
    def __init__(self, config: configparser.ConfigParser, iotcore: iotcore.IotCore):
        Thread.__init__(self, name="sender", daemon=True)
        self.config = config
        self.iotcore = iotcore
        
        self.database_connection = None
        self.last_timestamp_sent = 0

    def run(self):
        self.database_connection = database.Database.connect()
        self.iotcore.connect()
        while True:
            for p in database.PositionService.select_all_not_processed(self.database_connection):
                msg = iotcore.Message(
                    self.config['device']['id'],
                    p.timestamp,
                    p.latitude,
                    p.longitude,
                    p.speed
                )

                if p.timestamp - self.last_timestamp_sent >= 10:
                    self.iotcore.publish(msg)
                    self.last_timestamp_sent = p.timestamp
                    p.sent = True
                p.processed = True

                database.PositionService.update(self.database_connection, p)