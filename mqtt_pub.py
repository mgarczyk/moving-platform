from paho.mqtt import client as mqtt_client
import time

def connect_mqtt(client_id : str, broker : str, port : int ):
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def publish(client : str, topic : str, message):
    time.sleep(1)
    result = client.publish(topic, message)
    status = result[0]
    if status == 0:
        print(f"Send `{message}` to topic `{topic}`")
    else:
        print(f"Failed to send message to topic {topic}")

#Use code below to test pub<->sub communcation.

def test_run(client_id : str, broker : str, port : int , topic):
    client = connect_mqtt(client_id, broker, port)
    while True:
        publish(client, topic, "Message")

if __name__ == '__main__':
    client_id = f'subscribe-test'
    broker = 'localhost'
    port = 1883
    topic = "mqtt/test"
    test_run(client_id, broker, port, topic)

