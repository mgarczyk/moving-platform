import random
from paho.mqtt import client as mqtt_client

#Uncomment to use this script as subscriber 
#broker = 'localhost'
#port = 1883
#topic = "/home/radxa/moving_platform/mqtt/distance"
#client_id = f'subscribe-distance'

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

def subscribe(client: mqtt_client, topic):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
    client.subscribe(topic)
    client.on_message = on_message

def run():
    client = connect_mqtt(client_id, broker, port)
    subscribe(client, topic)
    client.loop_forever()

if __name__ == '__main__':
    run()
