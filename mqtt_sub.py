import random
from paho.mqtt import client as mqtt_client
import paho.mqtt.subscribe as subscribe

def connect_mqtt(client_id : str, broker : str, port : int) -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def subscribe_return_text(client: mqtt_client, topic : str):
    while True:
        msg = subscribe.simple(topic, hostname="localhost")
        return msg.payload.decode('utf-8')

def subscribe_save_image(client: mqtt_client, topic : str):
    def on_message(client, userdata, msg):
        open("opencv_sub.jpg", "wb").write(msg.payload)
    client.subscribe(topic)
    client.on_message = on_message

#Use code below to test pub<->sub communcation.

def test_run(client_id : mqtt_client, broker : str, port: int, topic: str):
    client = connect_mqtt(client_id, broker, port)
    while True:
        msg = subscribe.simple(topic, hostname="localhost")
        print("%s %s" % (msg.topic, msg.payload))
    
if __name__ == '__main__':
    client_id = "publish-test"
    broker = 'localhost'
    port = 1883
    topic = "mqtt/test"
    test_run(client_id, broker, port, topic)