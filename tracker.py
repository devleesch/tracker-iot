import logging
import uuid
import serial
import adafruit_gps
import config
import model
from diskcache import Deque


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)
class Tracker:
    def main(self):
        uart = serial.Serial(config.parser.get('device', 'serial'), baudrate=9600, timeout=10)
        gps = adafruit_gps.GPS(uart)

        gps.send_command(b'PMTK314,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
        hz = 10
        gps.send_command(str.encode(f'PMTK220,{1000 / hz}'))

        deque = Deque(directory="nmea")

        trip = str(uuid.uuid4())
        logger.info(f"starting trip {trip}")
        while True:
            #print(gps.readline())
            if gps.update() and gps.has_fix and gps.nmea_sentence.startswith("$GPRMC"):
                logger.info(f"lat: {gps.latitude} - lon: {gps.longitude}")
                deque.append(model.Message(uuid.uuid4(), gps.nmea_sentence, trip))

            try:
                message = deque.popleft()
                print(message.value)
            except Exception:
                pass


if __name__ == "__main__":
    tracker = Tracker()
    tracker.main()