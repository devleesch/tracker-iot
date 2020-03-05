import config
import persistqueue

import iotcore
import platform_detector
import sender

if platform_detector.is_rpi():
    import gps_uart as gps
    tty_gps = "/dev/serial0"
else:
    import gps_virtual as gps
    tty_gps = "data/track.nmea"

# configurations
device_id = config.device_id
update_interval = config.update_interval

project_id = "tracker-266917"
region = "europe-west1"
registry_id = "gps-tracker"
private_key_file = "pem/rsa_private.pem"
ca_certs = "pem/roots.pem"
algorithm = "RS256"
mqtt_hostname = "mqtt.googleapis.com"
mqtt_port = 443
topic_name = "nmea"
gps_to_send = ["$GPRMC"]


def main():
    queue = persistqueue.FIFOSQLiteQueue('./queue.sqlite', multithreading=True)
    client = iotcore.get_mqtt_client()

    g = gps.Gps(tty_gps, device_id, queue, update_interval)
    s = sender.Sender(queue, client)

    g.start()
    s.start()

if __name__ == "__main__":
    main()
