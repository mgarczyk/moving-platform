import time
import mqtt_pub
from periphery import GPIO
from paho.mqtt import client as mqtt_client
import paho.mqtt.subscribe as subscribe

ENCODER1_PIN_A = 74
ENCODER1_PIN_B = 158
DIR_R= 72

def on_message(client, obj, msg):
    global reset_encoders
    reset_encoders=1

def encoder_callback(pin_a, pin_b, topic):
    global reset_encoders
    tick_count = 0
    encoder_a = GPIO(pin_a, 'in')
    DIR = GPIO(DIR_R, 'in')
    encoder_b = GPIO(pin_b, 'in')
    prev_b_state = encoder_b.read()
    prev_value_a = encoder_a.read()
   
    while True:
        if reset_encoders==1:
            print(reset_encoders)
            tick_count=0
            reset_encoders=0
            time.sleep(0.2)
        dir_state=DIR.read()
        a_state = encoder_a.read()
        b_state = encoder_b.read()
        if a_state != prev_value_a or b_state != prev_b_state:
            if dir_state==0:
                tick_count += 1
            else:
                tick_count-=1
            prev_value_a = a_state
            prev_b_state = b_state
        mqtt_pub.publish(client, topic_pub, tick_count)
        time.sleep(0.05)

try:
    broker = 'localhost'
    port = 1883
    topic_pub = "mqtt/right_ticks"
    topic_sub = "mqtt/reset_encoders"
    client = mqtt_client.Client()
    client.connect(broker, port)
    client.subscribe(topic_sub ,0)
    client.on_message=on_message
    client.loop_start()

    reset_encoders=0

    encoder_callback(ENCODER1_PIN_A,ENCODER1_PIN_B, topic_pub)
        
except KeyboardInterrupt:
    pass
