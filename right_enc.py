import time
import json
from paho.mqtt import client as mqtt_client
from periphery import GPIO
import mqtt_pub

try:
    with open ("config.json") as config_f:
        config = json.load(config_f)
        ENCODER_LEFT_A = config["ENCODER_LEFT_A"]
        ENCODER_LEFT_B = config["ENCODER_LEFT_B"]
        BROKER = config["MQTT_BROKER"]
        PORT = config["MQTT_PORT"]
        config_f.close()
except FileNotFoundError:
    print("Brak pliku konfiguracyjnego.")
    exit()

def on_message(client, obj, msg):
    global reset_encoders
    if int(msg.payload.decode('utf8')) == 1:
        reset_encoders=1
        print(1)
    else:
        reset_encoders=0

def encoder_callback(pin_a, pin_b, topic):
    global reset_encoders
    tick_count = 0
    encoder_a = GPIO(pin_a, 'in')
    encoder_b = GPIO(pin_b, 'in')
    prev_b_state = encoder_b.read()
    prev_a_state = encoder_a.read()
    while True:
        if reset_encoders==1:
            tick_count=0
            reset_encoders=0
        a_state = encoder_a.read()
        b_state = encoder_b.read()
        if a_state != prev_a_state or b_state != prev_b_state:
                tick_count += 1
        prev_a_state = a_state
        prev_b_state = b_state
        mqtt_pub.publish(client, topic_pub, tick_count)
        time.sleep(0.05)

try:
    topic_pub = "mqtt/right_ticks"
    topic_sub = "mqtt/reset_encoders"
    client = mqtt_client.Client()
    client.connect(BROKER, PORT)
    client.subscribe(topic_sub, 0)
    client.on_message=on_message
    client.loop_start()
    reset_encoders=0
    encoder_callback(ENCODER_LEFT_A, ENCODER_LEFT_B, topic_pub)
except KeyboardInterrupt:
    pass