from threading import Thread

from persistqueue import FIFOSQLiteQueue
import paho.mqtt.client as mqttc

import iotcore

class Sender(Thread):
    def __init__(self, queue: FIFOSQLiteQueue, iotcore: iotcore.IotCore):
        Thread.__init__(self)
        self.queue = queue
        self.iotcore = iotcore

    def run(self):
        self.iotcore.connect()
        while True:
            msg = self.queue.get()
            self.iotcore.publish(msg)
