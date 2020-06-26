import config
import persistqueue

import iotcore
import sender
import gps

def main():
    queue = persistqueue.FIFOSQLiteQueue('./queue.sqlite', multithreading=True)
    client = iotcore.get_mqtt_client()

    g = gps.Gps(queue)
    s = sender.Sender(queue, client)

    g.start()
    s.start()

if __name__ == "__main__":
    main()
