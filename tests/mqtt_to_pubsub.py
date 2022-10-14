from enum import Flag
from http import client
from pydoc import cli
from re import M
from time import sleep
import paho.mqtt.client as mqtt
import paho.mqtt.properties as properties


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("connected with result code "+str(rc))
    client.subscribe("test/nmea", qos=1)

def on_connect5(client: mqtt.Client, userdata, flags, reasonCode, properties):
    print("connected with result code : {} - flags : {}".format(reasonCode, flags))
    client.subscribe("test/nmea", qos=1)

def on_message(client, userdata, message):
    print("{}".format(message.payload))

client = mqtt.Client(client_id="pubsub", protocol=mqtt.MQTTv5)
client.on_connect = on_connect5
client.on_message = on_message
client.tls_set()
client.username_pw_set("pubsub", "Fa&8Gv37gpL3X4YR")

props = mqtt.Properties(properties.PacketTypes.CONNECT)
props.SessionExpiryInterval = 30

client.connect("mqtt.neonweb.be", 8883, 60, clean_start=False, properties=props)    
print("listening...")
client.loop_forever()