from multiprocessing import Process
from time import sleep
import logging
from diskcache.persistent import Deque

import iotcore

logger = logging.getLogger(__name__)
class Sender(Process):
    def __init__(self, deque: Deque):
        Process.__init__(self, daemon=True)
        self.deque = deque
        self.iotcore = None

    def run(self):
        self.iotcore = iotcore.IotCore()
        self.iotcore.connect()
        while True:
            try:
                message = self.deque.popleft()
                self.iotcore.publish(message.to_json())
            except IndexError as e:
                sleep(5)
            except Exception as e:
                logger.error(e)
