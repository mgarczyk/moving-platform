import time
import periphery
import paho.mqtt.client as mqtt_client
import os
import math
import logging
import mqtt_pub
pwm_R = periphery.PWM(0, 0)
pwm_L = periphery.PWM(1, 0)
Dir_L_GPIO=periphery.GPIO(71,"out")
Dir_R_GPIO=periphery.GPIO(72,"out")
Dir_LIFT_GPIO=periphery.GPIO(157,"out")
PWM_LIFT_GPIO=periphery.GPIO(42,"out")
soft_start=True
#pwm_R.frequency=1e3
#pwm_L.frequency=1e3
pwm_L.enable()
pwm_R.enable()
data = -1
pomiar=True
distance_tmp= 0 
left_ticks=0
right_ticks=0
forw_dist=[]
rig_dist=[]
left_dist=[]
reverse_dist=[]
##LOGGER CONFIG##
FORMAT = '%(asctime)s - %(message)s'
logging.basicConfig(filename='auto_logger.log', filemode='w', level=logging.DEBUG, format=FORMAT)

def on_connect(client : mqtt_client, userdata, flags, rc):
    logging.info(f"Connected with result code: {str(rc)}")
    client.subscribe([("mqtt/left_ticks",0),("mqtt/right_ticks",1),("mqtt/lidar",2)])

def remove_zeroes_LIDAR(vector : list):
    for elements in vector:
        try:
            vector.remove(0)
        except:
            break
    return vector

def prepare_lidar_data(payload):
    text=str(payload)
    text=text[3:-2]
    distances=text.split(',')
    distances=[int(actual_shelf) for actual_shelf in distances]
    forw_dist=distances[150:210]
    rig_dist=distances[240:300]
    left_dist=distances[60:120]
    reverse_dist=distances[329:359]
    reverse_dist.extend(distances[0:30])
    remove_zeroes_LIDAR(forw_dist)
    logging.info(f'Forward distances: {forw_dist}')
    remove_zeroes_LIDAR(rig_dist)
    logging.info(f'Right distances: {rig_dist}')
    remove_zeroes_LIDAR(left_dist)
    logging.info(f'Left distances: {left_dist}')
    remove_zeroes_LIDAR(reverse_dist)
    logging.info(f'Reverse distances: {reverse_dist}')
    return forw_dist, rig_dist, left_dist, reverse_dist

def on_message(client : mqtt_client, obj, msg):
    global left_ticks, right_ticks, forw_dist, rig_dist, left_dist, reverse_dist
    if msg.topic=="mqtt/left_ticks":
        left_ticks = int(msg.payload.decode('utf8'))
        logging.info(f"Left ticks: {left_ticks}")
    elif msg.topic=="mqtt/right_ticks":
        right_ticks = int(msg.payload.decode('utf8'))
        logging.info(f"Right ticks: {right_ticks}")
    elif msg.topic=="mqtt/lidar":
        forw_dist, rig_dist, left_dist, reverse_dist = prepare_lidar_data(msg.payload)
        
def pwm_set_turn():
       pwm_R.duty_cycle = 0.5
       pwm_L.duty_cycle = 0.49

def pwm_set(soft_start : bool):
    if soft_start == True:
        for speed in [0.75,0.7,0.65,0.6,0.55,0.5,0.45,0.4,0.35,0.3,0.25]:
            pwm_R.duty_cycle = speed
            pwm_L.duty_cycle = speed
            time.sleep(0.07)
    soft_start=False
    return soft_start

def forward(soft_start : bool):
    # logging.info('### Forward selected ###')
    Dir_L_GPIO.write(False)
    Dir_R_GPIO.write(False)
    soft_start=pwm_set(soft_start)
    return soft_start

def back(soft_start : bool):
    logging.info('### Reverse selected ###')
    Dir_L_GPIO.write(True)
    Dir_R_GPIO.write(True)
    soft_start=pwm_set(soft_start)
    return soft_start

def left():
    logging.info('### Left selected ###')
    Dir_L_GPIO.write(False)
    Dir_R_GPIO.write(True)
    pwm_set_turn()

def right():
    logging.info('### Right selected ###')
    Dir_L_GPIO.write(True)
    Dir_R_GPIO.write(False)
    pwm_set_turn()

def lift():
    logging.info('### Lift going up ###')
    Dir_LIFT_GPIO.write(True)
    PWM_LIFT_GPIO.write(True)

def lower():
    logging.info('### Lift going down ###')
    Dir_LIFT_GPIO.write(False)
    PWM_LIFT_GPIO.write(True)

def stop():
    logging.info('### Stopped ###')
    lower()
    pwm_R.duty_cycle = 1.0
    pwm_L.duty_cycle = 1.0
    return True

def left_turn():
    left()
    time.sleep(3.75)
    stop()
    mqtt_pub.publish(client, "mqtt/reset_encoders", "1")
    time.sleep(0.1)

def right_turn():
    right()
    time.sleep(3.75)
    stop()
    mqtt_pub.publish(client, "mqtt/reset_encoders", "1")
    time.sleep(0.1)

def alley_init(dist_beetwen_measures : float):
    mqtt_pub.publish(client, "mqtt/reset_encoders", "1")
    time.sleep(0.1)
    global soft_start, distance_tmp
    soft_start=True
    distance_tmp=0
    next_measure_pos=dist_beetween_measures
    dystans_przeszkoda_szerokosc=0 
    dystans_szerokosc_temp=0
    dystans_przeszkoda_dlugosc=0
    return soft_start, distance_tmp, next_measure_pos, dystans_przeszkoda_szerokosc, dystans_szerokosc_temp, dystans_przeszkoda_dlugosc

def alley_drive(soft_start : bool, distance_tmp : float, dystans_przeszkoda_dlugosc : float):
    encoder_tick=(left_ticks+right_ticks)/2
    distance_tmp=dystans_przeszkoda_dlugosc+(encoder_tick/15)*math.pi*0.102    
    print(distance_tmp)
    soft_start=forward(soft_start)
    return soft_start, distance_tmp

def alley_measure(distance_tmp : float, dist_beetween_measures : float, next_measure_pos : float,  soft_start : bool):
    logging.info(f"Mesure distance: {distance_tmp}")
    soft_start=stop()
    lift()
    time.sleep(2)
    lower()
    time.sleep(2)
    next_measure_pos+=dist_beetween_measures
    return next_measure_pos, soft_start

def alley_end():
    stop()
    time.sleep(0.5)

def alley(distance_to_travel : float, dist_beetween_measures : float, is_measure : bool):
    soft_start, distance_tmp, next_measure_pos, dystans_przeszkoda_szerokosc, dystans_szerokosc_temp, dystans_przeszkoda_dlugosc = alley_init(dist_beetween_measures)
    #AVOIDING THE OBSTACLE#
    if any(forw_dist) < 1: 
        logging.warning("There is obstacle, starting to avoid it.")
        dystans_przeszkoda_szerokosc=0
        dystans_szerokosc_temp=0
        dystans_przeszkoda_dlugosc=0
        left_turn()  # skret w lewo po wykryciu przeszkody
        while any(rig_dist)<80: # jazda prosto do konca przeszkody - wolnego miejsca po prawej 
            if any(forw_dist)<55:
                logging.error("Can't avoid STOP.")
                stop()
                exit()
            encoder_tick=(left_ticks+right_ticks)/2
            dystans_przeszkoda_szerokosc=(encoder_tick/15)*math.pi*0.102 # droga pokonana na szerokosc 
            soft_start=forward(soft_start) # jazda do przodu do momentu spelnienia warunku
        right_turn() # koniec przeszkody 
        while any(rig_dist)<80: # jazda na długosc 
            if any(forw_dist)<55:
                logging.error("Can't avoid STOP.")
                stop()
                exit()
            encoder_tick=(left_ticks+right_ticks)/2
            dystans_przeszkoda_dlugosc=(encoder_tick/15)*math.pi*0.102
            soft_start=forward(soft_start)
        right_turn() # powrot na srodek sciezki
        while dystans_szerokosc_temp<=dystans_przeszkoda_szerokosc:
            encoder_tick=(left_ticks+right_ticks)/2
            dystans_szerokosc_temp=(encoder_tick/15)*math.pi*0.102
            soft_start=forward(soft_start)
        left_turn()
    else:
        ##DRIVING WHEN THERE ARE NO OBSTACLES##
        while distance_tmp<distance_to_travel:
            soft_start, distance_tmp = alley_drive(soft_start, distance_tmp, dystans_przeszkoda_dlugosc)
            if distance_tmp>=next_measure_pos and is_measure==True:
                next_measure_pos, soft_start = alley_measure(distance_tmp, dist_beetween_measures, next_measure_pos, soft_start)
                    
def curve(route : str, shelf_width : float):
    mqtt_pub.publish(client, "mqtt/reset_encoders", "1")
    if route=='P':
        left_turn()
        alley(shelf_width, 1, False)
        alley_end()
        left_turn()
        return 'L'
    elif route=='L':
        right_turn()
        alley(shelf_width, 1, False)
        alley_end()
        right_turn()
        return 'P'        

def user_input():
    while True:
        try:
            length_of_alley=float(input("Podaj długość magazynu w [m]: "))
            break
        except ValueError:
            print("Podaj ponownie")
    while True:
        try:
            shelf_width=float(input("Podaj szerokość regału w [m]: "))
            break
        except ValueError:
            print("Podaj ponownie")
    while True:
        try:
            dist_beetween_measures=float(input("Podaj dystans między pomiarami: "))
            break
        except ValueError:
            print("Podaj ponownie")
    while True:
        try:
            number_of_shelfs=int(input("Podaj ilośc regałów: "))
            break
        except ValueError:
            print("Podaj ponownie")
    while True:
        try:
            route=input("Podaj po której stronie robota jest ściana (L / P)")
            if route in ['L', 'P']:
                break
            raise ValueError
        except ValueError:
            print("Podaj ponownie.")
    return length_of_alley, shelf_width, number_of_shelfs, route, dist_beetween_measures

if __name__ == '__main__':
    logging.info("====================")
    logging.info('-----New sesion-----')
    logging.info("====================")  
    client = mqtt_client.Client()
    client.on_connect=on_connect
    client.on_message=on_message
    client.connect("localhost", 1883)
    client.loop_start()
    length_of_alley, shelf_width, number_of_shelfs, route, dist_beetween_measures = user_input()
    actual_shelf=0
    left_ticks=0
    right_ticks=0
    while actual_shelf<=number_of_shelfs:
        try:
                mqtt_pub.publish(client, "mqtt/reset_encoders", "1")
                time.sleep(0.3)
                alley(length_of_alley, dist_beetween_measures, True)
                stop()
                soft_start=True
                lift_flag=True
                actual_shelf=actual_shelf+1
                if actual_shelf<=number_of_shelfs:
                    route=curve(route,shelf_width) 
        except KeyboardInterrupt:
            stop()
            logging.info('-----Manual exit-----')
            exit()
    stop() 
    distance_tmp=0