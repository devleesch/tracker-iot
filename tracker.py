import gps
import time
import logging
from sender import Sender
from diskcache import Deque
import config


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)
class Tracker:
    def main(self):
        deque = Deque(directory="nmea")

        t_sender = Sender(deque)
        t_sender.start()

        if config.parser.getboolean('device', 'track_mode'):
            t_gps = gps.GpsTrack(deque)
        else:
            t_gps = gps.GpsRoad(deque)
        t_gps.start()

        while True:
            time.sleep(1)


if __name__ == "__main__":
    tracker = Tracker()
    tracker.main()