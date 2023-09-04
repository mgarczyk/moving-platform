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
    msg = subscribe.simple(topic, hostname='localhost')
    return msg.payload.decode('utf-8')

def subscribe_save_image(client: mqtt_client, topic : str):
    def on_message(client, userdata, msg):
        open("opencv_sub.jpg", "wb").write(msg.payload)
    client.subscribe(topic)
    client.on_message = on_message

def subscribe_text_loop(client: mqtt_client, topic : str):
    def on_message(client, userdata, msg):
        print(msg.payload)
    client.subscribe(topic)
    client.on_message = on_message
    client.loop_forever()

#Use code below to test pub<->sub communcation.

def test_run(client_id : mqtt_client, broker : str, port: int, topic: str):
    client = connect_mqtt(client_id, broker, port)
    subscribe_text_loop(client, topic)
    
if __name__ == '__main__':
    client_id = "subscribe-test"
    broker = 'localhost'
    port = 8883 #on rock 1883
    topic = "mqtt/steering" 
    try:
        test_run(client_id, broker, port, topic)
    except KeyboardInterrupt:
        print("Connection ended")
        exit()
