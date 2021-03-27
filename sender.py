from threading import Thread
from time import sleep
from diskcache import Deque

import iotcore
import model


class Sender(Thread):
    def __init__(self, iotcore: iotcore.IotCore):
        Thread.__init__(self, name="sender", daemon=True)
        self.iotcore = iotcore

    def run(self):
        deque = Deque(directory="nmea")
        self.iotcore.connect()
        while True:
            try:
                message = deque.popleft()
                self.iotcore.publish(message.to_json())
            except IndexError:
                sleep(1)
            except Exception as e:
                print(e)
        self.iotcore.disconnect()
