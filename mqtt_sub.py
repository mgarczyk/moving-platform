import random
from paho.mqtt import client as mqtt_client

def connect_mqtt(client_id, broker, port) -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def subscribe_text(client: mqtt_client, topic):
    def on_message(client, userdata, msg):
         print(f"Received `{msg.payload}` from `{msg.topic}` topic")
    client.subscribe(topic)
    client.on_message = on_message

def subscribe_image(client: mqtt_client, topic):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload}` from `{msg.topic}` topic")
        open("opencv_sub.jpg", "wb").write(msg.payload)
    client.subscribe(topic)
    client.on_message = on_message

def run(client_id, broker, port, topic):
    client = connect_mqtt(client_id, broker, port)
    subscribe_text(client, topic)
    client.loop_forever()

if __name__ == '__main__':
    client_id = "X"
    broker = 'localhost'
    port = 1883
    topic = "mqtt/steering"
    run(client_id, broker, port, topic)
