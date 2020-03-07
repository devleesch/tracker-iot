from threading import Thread

from persistqueue import FIFOSQLiteQueue
import paho.mqtt.client as mqttc

import iotcore
import tracker


class Sender(Thread):
    def __init__(self, queue: FIFOSQLiteQueue, client: mqttc):
        Thread.__init__(self)
        self.queue = queue
        self.client = client

    def run(self):
        iotcore.authenticate(self.client)
        iotcore.connect(self.client)
        while True:
            msg = self.queue.get()
            iotcore.publish(self.client, msg)
