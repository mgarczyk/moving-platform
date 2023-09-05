import time
import mqtt_pub
from periphery import GPIO

ENCODER1_PIN_A = 74
ENCODER1_PIN_B = 158
DIR_R= 72



def encoder_callback(pin_a, pin_b):
    client = mqtt_pub.connect_mqtt("encoder_R", "localhost", 1883)
    
    tick_count = 0
    encoder_a = GPIO(pin_a, 'in')
    DIR = GPIO(DIR_R, 'in')
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
        mqtt_pub.publish(client, "mqtt/right_ticks", tick_count)
        time.sleep(0.05)


try:
    encoder_callback(ENCODER1_PIN_A,ENCODER1_PIN_B)
        
except KeyboardInterrupt:
    pass