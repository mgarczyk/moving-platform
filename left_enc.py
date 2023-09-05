import time
import mqtt_pub
from periphery import GPIO

ENCODER2_PIN_A = 76
ENCODER2_PIN_B = 73
DIR_L=71


def encoder_callback(pin_a, pin_b):
    client = mqtt_pub.connect_mqtt("encoder_L", "localhost", 1883)
    
    tick_count = 0
    encoder_a = GPIO(pin_a, 'in')
    DIR = GPIO(DIR_L, 'in')
    encoder_b = GPIO(pin_b, 'in')
    prev_b_state = encoder_b.read()
    prev_value_a = encoder_a.read()
   
    while True:
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

            # Tutaj możesz umieścić swoje własne operacje lub wyświetlić wynik
        mqtt_pub.publish(client, "mqtt/left_ticks", tick_count)
        time.sleep(0.05)


try:
    encoder_callback(ENCODER2_PIN_A,ENCODER2_PIN_B)
        
except KeyboardInterrupt:
    pass
