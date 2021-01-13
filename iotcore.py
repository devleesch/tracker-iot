import datetime
import time
import ssl
import jwt
import paho.mqtt.client as mqttc

import config


class IotCore:
    def __init__(self):
        self.client = IotCore.build_mqtt_client()

    def connect(self):
        while not self.client.is_connected():
            try:
                self.client.connect(config.parser['gcp']['mqtt_hostname'], int(config.parser['gcp']['mqtt_port']))
                self.client.loop_start()
                break
            except Exception as e:
                print("waiting for network connection...")
                time.sleep(10)

    def publish(self, message: str):
        info = self.client.publish("/devices/{}/events".format(config.parser['device']['id']), message, qos=1)
        info.wait_for_publish()
        print("published {}".format(message))
        
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
        client.on_connect = IotCore.on_connect
        client.on_disconnect = IotCore.on_disconnect
        IotCore.authenticate(client)

        return client

    @staticmethod
    def create_jwt(clients: mqttc.Client):
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
        print("on_connect: {}".format(mqttc.connack_string(rc)))
        if rc == mqttc.CONNACK_REFUSED_BAD_USERNAME_PASSWORD:
            print("JWT token expired. Update token.")
            IotCore.authenticate(client)

    @staticmethod
    def on_disconnect(client, userdata, rc):
        print("on_disconnect: {}".format(mqttc.connack_string(rc)))

    @staticmethod
    def authenticate(client: mqttc):
        client.username_pw_set("unused", IotCore.create_jwt(client))