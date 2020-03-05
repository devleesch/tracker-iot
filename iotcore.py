import datetime
import time
import ssl

import jwt
import paho.mqtt.client as mqttc

import tracker


def get_mqtt_client(project_id, region, registry_id, device_id, ca_certs):
    client_id = "projects/{}/locations/{}/registries/{}/devices/{}".format(project_id, region,
                                                                           registry_id, device_id)
    client = mqttc.Client(client_id=client_id)
    client.tls_set(ca_certs=ca_certs, tls_version=ssl.PROTOCOL_TLSv1_2)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    return client


def create_jwt(project_id, private_key_file, algorithm: str):
    now = datetime.datetime.utcnow()
    claims = {
        'iat': now,
        'exp': (now + datetime.timedelta(minutes=60)),
        'aud': project_id
    }

    with open(private_key_file, "rb") as f:
        private_key = f.read()

    return jwt.encode(claims, private_key, algorithm=algorithm)


def connect(client: mqttc):
    while not client.is_connected():
        try:
            client.connect(tracker.mqtt_hostname, tracker.mqtt_port)
            client.loop_start()
            break
        except:
            print("waiting for network connection...")
            time.sleep(10)


def on_connect(client: mqttc, userdata, flag, rc: str):
    print("on_connect: {}".format(mqttc.connack_string(rc)))
    if rc == mqttc.CONNACK_REFUSED_BAD_USERNAME_PASSWORD:
        print("JWT token expired. Update token.")
        authenticate(client, create_jwt(tracker.project_id, tracker.private_key_file, tracker.algorithm))


def on_disconnect(client, userdata, rc):
    print("on_disconnect: {}".format(mqttc.connack_string(rc)))


def publish(client, device_id, msg: str):
    info = client.publish("/devices/{}/events".format(device_id), msg, qos=1)
    info.wait_for_publish()
    print("published {} : {}".format(info.mid, msg))


def authenticate(client: mqttc, token: str):
    client.username_pw_set("unused", token)
