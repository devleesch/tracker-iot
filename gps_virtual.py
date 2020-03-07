from threading import Thread
import time
from datetime import datetime, timedelta
from persistqueue import FIFOSQLiteQueue

import message
import tracker


class Gps(Thread):

    def __init__(self, path, device_id: str, queue: FIFOSQLiteQueue, interval: int):
        Thread.__init__(self)
        self.path = path
        self.device_id = device_id
        self.queue = queue
        self.interval = interval
        self.lastMessageTime = datetime.now() - timedelta(milliseconds=interval)

    def run(self):
        with open(self.path) as f:
            while True:
                l = f.readline().rstrip()
                if not l:
                    break

                if l.split(",")[0] in tracker.gps_to_send:
                    now = datetime.now()
                    if now - self.lastMessageTime > timedelta(milliseconds=self.interval):
                        msg = message.Message(self.device_id, l)
                        print("queueing {}".format(msg.to_json()))
                        self.queue.put(msg.to_json())
                        self.lastMessageTime = now
                time.sleep(0.1)
        print("end of GPS file")
