import time
import math
import mqtt_pub
import mqtt_sub
from periphery import GPIO

ENCODER1_PIN_A = 74
ENCODER1_PIN_B = 158
encoder_right_a = GPIO(ENCODER1_PIN_A, "in")
encoder_right_b = GPIO(ENCODER1_PIN_B, "in")
right_ticks=0

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
        change_count_right = read_encoder_speed(encoder_right_a, encoder_right_b)
        right_ticks+=change_count_right
        print( "Right:",right_ticks)
        mqtt_pub.publish(client, "mqtt/right_ticks", right_ticks)
except KeyboardInterrupt:
    pass