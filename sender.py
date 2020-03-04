from threading import Thread

from persistqueue import FIFOSQLiteQueue
import paho.mqtt.client as mqttc

import iotcore
import tracker


class Sender(Thread):
    def __init__(self, queue: FIFOSQLiteQueue, client: mqttc):
        Thread.__init__(self)
        self.name = "sender"
        self.queue = queue
        self.client = client

    def run(self):
        token = iotcore.create_jwt(tracker.project_id, tracker.private_key_file, tracker.algorithm)
        iotcore.authenticate(self.client, token)
        iotcore.connect(self.client)
        while True:
            msg = self.queue.get()
            iotcore.publish(self.client, tracker.device_id, msg)
