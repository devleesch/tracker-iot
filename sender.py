import datetime
import logging
import ssl
import time
from cmath import log
from multiprocessing import Process

import jwt
import paho.mqtt.client as mqttc
from diskcache.persistent import Deque
from google.cloud import pubsub_v1

import config

logger = logging.getLogger(__name__)
class Sender(Process):
    def __init__(self, deque: Deque):
        Process.__init__(self, daemon=True)
        self.deque = deque


class SenderIotCore(Sender):
    def __init__(self, deque: Deque):
        super().__init__(deque)
        self.client = None


    def run(self):
        self.client = SenderIotCore.build_mqtt_client()
        self.connect()
        while True:
            try:
                message = self.deque.popleft()
                self.client.publish(message.to_json())
            except IndexError as e:
                time.sleep(5)
            except Exception as e:
                logger.error(e)


    def connect(self):
        while not self.client.is_connected():
            try:
                self.client.connect(config.parser['gcp']['mqtt_hostname'], int(config.parser['gcp']['mqtt_port']))
                self.client.loop_start()
                break
            except Exception as e:
                logger.info("waiting for network connection...")
                time.sleep(10)


    def publish(self, message: str):
        info = self.client.publish("/devices/{}/events".format(config.parser['device']['id']), message, qos=1)
        info.wait_for_publish()
        logger.info("published {}".format(message))


    def disconnect(self):
        self.client.disconnect()
        self.client.loop_stop()
        

    @staticmethod
    def build_mqtt_client() -> mqttc.Client:
        client_id = "projects/{}/locations/{}/registries/{}/devices/{}".format(
            config.parser['gcp']['project_id'],
            config.parser['gcp']['region'],
            config.parser['gcp']['registry_id'], 
            config.parser['device']['id']
        )
        client = mqttc.Client(client_id=client_id)
        client.tls_set(ca_certs=config.parser['device']['ca_certs'], tls_version=ssl.PROTOCOL_TLSv1_2)
        client.on_connect = SenderIotCore.on_connect
        client.on_disconnect = SenderIotCore.on_disconnect
        client.username_pw_set("unused", SenderIotCore.create_jwt())

        return client


    @staticmethod
    def create_jwt():
        now = datetime.datetime.utcnow()
        claims = {
            'iat': now,
            'exp': (now + datetime.timedelta(minutes=60)),
            'aud': config.parser['gcp']['project_id']
        }

        with open(config.parser['device']['private_key_file'], "rb") as f:
            private_key = f.read()

        return jwt.encode(claims, private_key, algorithm=config.parser['gcp']['algorithm'])


    @staticmethod
    def on_connect(client: mqttc, userdata, flag, rc: str):
        logger.info("on_connect: {}".format(mqttc.connack_string(rc)))
        if rc == mqttc.CONNACK_REFUSED_BAD_USERNAME_PASSWORD:
            logger.warning("JWT token expired. Update token.")
            client.username_pw_set("unused", SenderIotCore.create_jwt())


    @staticmethod
    def on_disconnect(client, userdata, rc):
        logger.info("on_disconnect: {}".format(mqttc.connack_string(rc)))


project_id = "tracker-266917"
topic_id = "nmea"
class SenderPubSub(Sender):
    def __init__(self, deque: Deque):
        super().__init__(deque)

    
    def run(self):
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(project_id, topic_id)
        while(True):
            try:
                if len(self.deque):
                    message = self.deque.popleft()
                    print("processing {}".format(message))
                    publisher.publish(topic_path, message.encode("utf-8"))
                else:
                    time.sleep(1)
            except Exception as e:
                logger.error("unexpected error", e)
