import time
import math
import mqtt_pub
import mqtt_sub
from periphery import GPIO

ENCODER2_PIN_A = 76
ENCODER2_PIN_B = 73
encoder_left_a = GPIO(ENCODER2_PIN_A, "in")
encoder_left_b = GPIO(ENCODER2_PIN_B, "in")
left_ticks=0

def read_encoder_speed(gpio_a, gpio_b):
    prev_value_a = gpio_a.read()
    prev_value_b = gpio_b.read()
    change_count = 0
    start_time = time.time()
    while True:
        current_value_a = gpio_a.read()
        current_value_b = gpio_b.read()
        if current_value_a != prev_value_a or current_value_b != prev_value_b:
            change_count += 1
            prev_value_a = current_value_a
            prev_value_b = current_value_b
            return change_count
try:
    while True:
        client = mqtt_pub.connect_mqtt("encoder", "localhost", 1883)
        change_count_left = read_encoder_speed(encoder_left_a, encoder_left_b)
        left_ticks+=change_count_left
        print("Left:", left_ticks)
        mqtt_pub.publish(client, "mqtt/left_ticks", left_ticks)
except KeyboardInterrupt:
    pass