import datetime
import time
import ssl

import jwt
import paho.mqtt.client as mqttc

import configparser


class IotCore:

    config = None

    def __init__(self, config: configparser.ConfigParser):
        IotCore.config = config
        self.client = IotCore.build_mqtt_client()


    def connect(self):
        while not self.client.is_connected():
            try:
                self.client.connect(IotCore.config['gcp']['mqtt_hostname'], int(IotCore.config['gcp']['mqtt_port']))
                self.client.loop_start()
                break
            except Exception as e:
                print("waiting for network connection...")
                time.sleep(10)


    def publish(self, msg: str):
        info = self.client.publish("/devices/{}/events".format(IotCore.config['device']['id']), msg, qos=1)
        info.wait_for_publish()
        print("published {}".format(msg))
        

    @staticmethod
    def build_mqtt_client() -> mqttc.Client:
        client_id = "projects/{}/locations/{}/registries/{}/devices/{}".format(
            IotCore.config['gcp']['project_id'],
            IotCore.config['gcp']['region'],
            IotCore.config['gcp']['registry_id'], 
            IotCore.config['device']['id']
        )
        client = mqttc.Client(client_id=client_id)
        client.tls_set(ca_certs=IotCore.config['device']['ca_certs'], tls_version=ssl.PROTOCOL_TLSv1_2)
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
            'aud': IotCore.config['gcp']['project_id']
        }

        with open(IotCore.config['device']['private_key_file'], "rb") as f:
            private_key = f.read()

        token = jwt.encode(claims, private_key, algorithm=IotCore.config['gcp']['algorithm']) 
        print("create_jwt: {}", token)
        return token


    @staticmethod
    def on_connect(client: mqttc, userdata, flag, rc: str):
        print("on_connect: {}".format(mqttc.connack_string(rc)))
        if rc == mqttc.CONNACK_REFUSED_BAD_USERNAME_PASSWORD:
            print("JWT token expired. Update token.")
            authenticate(client)


    @staticmethod
    def on_disconnect(client, userdata, rc):
        print("on_disconnect: {}".format(mqttc.connack_string(rc)))


    @staticmethod
    def authenticate(client: mqttc):
        client.username_pw_set("unused", IotCore.create_jwt(client))
