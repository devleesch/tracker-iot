import datetime
import time
import ssl

import jwt
import paho.mqtt.client as mqttc

import config


def get_mqtt_client() -> mqttc.Client:
    client_id = "projects/{}/locations/{}/registries/{}/devices/{}".format(config.project_id, config.region,
                                                                           config.registry_id, config.device_id)
    client = mqttc.Client(client_id=client_id)
    client.tls_set(ca_certs=config.ca_certs, tls_version=ssl.PROTOCOL_TLSv1_2)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    return client


def create_jwt():
    now = datetime.datetime.utcnow()
    claims = {
        'iat': now,
        'exp': (now + datetime.timedelta(minutes=60)),
        'aud': config.project_id
    }

    with open(config.private_key_file, "rb") as f:
        private_key = f.read()

    return jwt.encode(claims, private_key, algorithm=config.algorithm)


def connect(client: mqttc):
    while not client.is_connected():
        try:
            client.connect(config.mqtt_hostname, config.mqtt_port)
            client.loop_start()
            break
        except:
            print("waiting for network connection...")
            time.sleep(10)


def on_connect(client: mqttc, userdata, flag, rc: str):
    print("on_connect: {}".format(mqttc.connack_string(rc)))
    if rc == mqttc.CONNACK_REFUSED_BAD_USERNAME_PASSWORD:
        print("JWT token expired. Update token.")
        authenticate(client)


def on_disconnect(client, userdata, rc):
    print("on_disconnect: {}".format(mqttc.connack_string(rc)))


def publish(client, msg: str):
    info = client.publish("/devices/{}/events".format(config.device_id), msg, qos=1)
    info.wait_for_publish()
    print("published {}".format(msg))


def authenticate(client: mqttc):
    client.username_pw_set("unused", create_jwt())
