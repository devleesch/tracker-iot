from http import client
from pydoc import cli
from time import sleep
import paho.mqtt.client as mqtt


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("connected with result code "+str(rc))

def on_connect5(client, userdata, flags, reasonCode, properties):
    print("connected with result code "+str(reasonCode))

client = mqtt.Client(protocol=mqtt.MQTTv5)
client.on_connect = on_connect5
client.tls_set()
client.username_pw_set("rpi-tracker", "JHhkj=k!jHKJhi5")

client.connect("mqtt.neonweb.be", 8883, 60)
client.loop_start()

count = 0
while(True):
    while(not client.is_connected()):
        print("waiting connection to MQTT broker...")
        sleep(1)

    while(client.is_connected()):
        msg = "MSG#{}".format(count)
        msg_info = client.publish("test/nmea", qos=1, payload=msg)
        msg_info.wait_for_publish()
        print("{} sent".format(msg))
        count += 1
        sleep(1)