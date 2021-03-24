import logging
import sqlite3
import uuid
import serial
import adafruit_gps
import config


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)
class Tracker:
    def main(self):
        uart = serial.Serial(config.parser.get('device', 'serial'), baudrate=9600, timeout=10)
        gps = adafruit_gps.GPS(uart)
        db = sqlite3.connect("test.db")
        db.executescript("""
            create table if not exists nmea(
                uuid TEXT NOT NULL PRIMARY KEY,
                value TEXT NOT NULL,
                trip TEXT NOT NULL
            );
        """)

        trip = str(uuid.uuid4())
        logger.info(f"starting trip {trip}")
        while True:
            #print(gps.readline())
            if gps.update() and gps.has_fix and gps.nmea_sentence.startswith("$GPRMC"):
                logger.info(f"lat: {gps.latitude} - lon: {gps.longitude}")
                db.execute("""
                    insert into nmea values(?, ?, ?)
                """, [str(uuid.uuid4()), gps.nmea_sentence, trip])
                db.commit()

if __name__ == "__main__":
    tracker = Tracker()
    tracker.main()