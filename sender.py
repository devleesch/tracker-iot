from threading import Thread
from time import sleep
from diskcache import Deque

import iotcore


class Sender(Thread):
    def __init__(self, deque: Deque):
        Thread.__init__(self, name="sender", daemon=True)
        self.deque = deque
        self.iotcore = iotcore.IotCore()

    def run(self):
        self.iotcore.connect()
        while True:
            try:
                message = self.deque.popleft()
                self.iotcore.publish(message.to_json())
            except IndexError:
                sleep(5)
            except Exception as e:
                print(e)
