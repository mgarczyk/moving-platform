from paho.mqtt import client as mqtt_client
import time


def connect_mqtt(client_id, broker, port):
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def publish(client, topic, message):
    time.sleep(1)
    result = client.publish(topic, message)
    status = result[0]
    if status == 0:
        print(f"Send `{message}` to topic `{topic}`")
    else:
        print(f"Failed to send message to topic {topic}")


def run(client_id, broker, port, topic):
    client = connect_mqtt(client_id, broker, port)
    client.loop_start()
    publish(client, topic, "Message")
    client.loop_stop()

if __name__ == '__main__':
    client_id = f'subscribe-distance'
    broker = 'localhost'
    port = 1883
    topic = "/home/radxa/moving_platform/mqtt/test"
    run(client_id, broker, port, topic)

