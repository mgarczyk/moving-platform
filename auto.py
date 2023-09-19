import time
import periphery
import paho.mqtt.client as mqtt_client
import os
import math
import logging
import mqtt_pub
import serial
PWM_motor = periphery.PWM(0, 0)
Dir_L_GPIO=periphery.GPIO(71,"out")
Dir_R_GPIO=periphery.GPIO(72,"out")
Dir_LIFT_GPIO=periphery.GPIO(157,"out")
PWM_LIFT_GPIO=periphery.GPIO(42,"out")
soft_start=True
PWM_motor.enable()
data = -1
pomiar=True
distance_tmp= 0 
left_ticks=0
right_ticks=0    
forw_dist=[]
rig_dist=[]
left_dist=[]
reverse_dist=[]
us_100=[]
##LOGGER CONFIG##
FORMAT = '%(asctime)s - %(message)s'
logging.basicConfig(filename='auto_logger.log', filemode='w', level=logging.DEBUG, format=FORMAT)

def on_connect(client : mqtt_client, userdata, flags, rc):
    logging.info(f"Connected to broker with result code: {str(rc)}")
    client.subscribe([("mqtt/left_ticks",1),("mqtt/right_ticks",1),("mqtt/lidar",0),("mqtt/distance",0)])

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
    forw_dist=distances[170:190]
    rig_dist=distances[250:290]
    left_dist=distances[60:120]
    reverse_dist=distances[329:359]
    reverse_dist.extend(distances[0:30])
    remove_zeroes_LIDAR(forw_dist)
    remove_zeroes_LIDAR(rig_dist)
    remove_zeroes_LIDAR(left_dist)
    remove_zeroes_LIDAR(reverse_dist)
    return forw_dist, rig_dist, left_dist, reverse_dist

def prepare_us100_data(payload):
    text=str(payload)
    text=text[3:-2]
    distances=text.split(',')
    distances=[int(actual_shelf) for actual_shelf in distances]
    us_100=distances[0:4]
    return us_100

def on_message(client : mqtt_client, obj, msg):
    global left_ticks, right_ticks, forw_dist, rig_dist, left_dist, reverse_dist, us_100
    if msg.topic=="mqtt/left_ticks":
        left_ticks = int(msg.payload.decode('utf8'))
    elif msg.topic=="mqtt/right_ticks":
        right_ticks = int(msg.payload.decode('utf8'))
    elif msg.topic=="mqtt/lidar":
        forw_dist, rig_dist, left_dist, reverse_dist = prepare_lidar_data(msg.payload)
    elif msg.topic=="mqtt/distance":
        us_100 = prepare_us100_data(msg.payload)
        
def pwm_set_turn():
       PWM_motor.duty_cycle = 0.5

def pwm_set(soft_start : bool):
    if soft_start == True:
        for speed in [0.7,0.65,0.6,0.55,0.5,0.45,0.4,0.35,0.3,0.25]:
            PWM_motor.duty_cycle = speed
            time.sleep(0.07)
    else:
        PWM_motor.duty_cycle = 0.25
    soft_start=False
    return soft_start

def forward(soft_start : bool):
    ser.write(b"forward\n")
    # Dir_L_GPIO.write(False)
    # Dir_R_GPIO.write(False)
    # soft_start=pwm_set(soft_start)
     #return soft_start

def back(soft_start : bool):
    ser.write(b"back\n")

    # Dir_L_GPIO.write(True)
    # Dir_R_GPIO.write(True)
    # soft_start=pwm_set(soft_start)
    # return soft_start

def left():
        ser.write(b"left\n")

    # Dir_L_GPIO.write(False)
    # Dir_R_GPIO.write(True)
    # pwm_set_turn()

def right():
        ser.write(b"right\n")

    # Dir_L_GPIO.write(True)
    # Dir_R_GPIO.write(False)
    # pwm_set_turn()

def lift():
    Dir_LIFT_GPIO.write(True)
    PWM_LIFT_GPIO.write(True)

def lower():
    Dir_LIFT_GPIO.write(False)
    PWM_LIFT_GPIO.write(True)

def stop():
        ser.write(b"stop\n")

    # lower()
    # PWM_motor.duty_cycle = 1.0
    # return True

def left_turn():
    left()
    time.sleep(3.85)
    stop()
    mqtt_pub.publish(client, "mqtt/reset_encoders", "1")
    time.sleep(0.1)

def right_turn():
    right()
    time.sleep(3.9)
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
    sumaryczna_dlugosc_przeszkod = 0
    return soft_start, distance_tmp, next_measure_pos, sumaryczna_dlugosc_przeszkod

def alley_drive( distance_tmp : float, sumaryczna_dlugosc_przeszkod : float):
    encoder_tick=(left_ticks+right_ticks)/2
    distance_tmp = sumaryczna_dlugosc_przeszkod + (encoder_tick/14.85)*math.pi*0.102    
    print(distance_tmp)
    forward(soft_start)
    return distance_tmp

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
    soft_start, distance_tmp, next_measure_pos, sumaryczna_dlugosc_przeszkod = alley_init(dist_beetween_measures)
    while distance_tmp<distance_to_travel:
    #     #AVOIDING THE OBSTACLE#
    #     if any(x<60 for x in forw_dist) or any(y<30 for y in us_100):
    #         szerokosc_przeszkody = 0
    #         szerokosc_przeszkody_powrot = 0
    #         dlugosc_przeszkody = 0
    #         if us_100[2]<30 or us_100[3]<30 :
    #             logging.info(f"Avoiding obstacle from right side.")
    #             left_turn()  # skret w lewo po wykryciu przeszkody
    #             while any(x<80 for x in rig_dist): # jazda prosto do konca przeszkody - wolnego miejsca po prawej 
    #                 if any(x<50 for x in us_100):
    #                     logging.info("Can't avoid STOP.")
    #                     stop()
    #                     exit()
    #                 encoder_tick=(left_ticks+right_ticks)/2
    #                 szerokosc_przeszkody=(encoder_tick/15)*math.pi*0.102 # droga pokonana na szerokosc
    #                 soft_start=forward(soft_start) # jazda do przodu do momentu spelnienia warunku
    #             logging.info(f"Obstacle width: {szerokosc_przeszkody}")
    #             right_turn() # koniec przeszkody 
    #             while any(x<80 for x in rig_dist): # jazda na długosc 
    #                 #print(forw_dist)
    #                 if any(x<50 for x in us_100):
    #                     logging.error("Can't avoid STOP.")
    #                     stop()
    #                     exit()
    #                 encoder_tick=(left_ticks+right_ticks)/2
    #                 dlugosc_przeszkody=(encoder_tick/15)*math.pi*0.102
    #                 soft_start=forward(soft_start)
    #             sumaryczna_dlugosc_przeszkod += dlugosc_przeszkody
    #             logging.info(f"Obstacle length: {dlugosc_przeszkody}")
    #             right_turn() # powrot na srodek sciezki
    #             while szerokosc_przeszkody_powrot<=szerokosc_przeszkody:
    #                 encoder_tick=(left_ticks+right_ticks)/2
    #                 szerokosc_przeszkody_powrot=(encoder_tick/15)*math.pi*0.102
    #                 soft_start=forward(soft_start)
    #             left_turn()
    #             logging.info(f"Obstacle avoided.")
    #         else:
    #             logging.warning(f"Avoiding obstacle from left side.")
    #             right_turn()
    #             while any(x<80 for x in left_dist): # jazda prosto do konca przeszkody - wolnego miejsca po prawej 
    #                 if any(x<50 for x in us_100):
    #                     logging.error("Can't avoid STOP.")
    #                     stop()
    #                     exit()
    #                 encoder_tick=(left_ticks+right_ticks)/2
    #                 szerokosc_przeszkody=(encoder_tick/15)*math.pi*0.102 # droga pokonana na szerokosc 
    #                 soft_start=forward(soft_start) # jazda do przodu do momentu spelnienia warunku
    #             logging.info(f"Obstacle width: {szerokosc_przeszkody}")
    #             left_turn() # koniec przeszkody 
    #             while any(x<80 for x in left_dist): # jazda na długosc 
    #                 #print(forw_dist)
    #                 if any(x<50 for x in us_100):
    #                     logging.error("Can't avoid STOP.")
    #                     stop()
    #                     exit()
    #                 encoder_tick=(left_ticks+right_ticks)/2
    #                 dlugosc_przeszkody=(encoder_tick/15)*math.pi*0.102
    #                 soft_start=forward(soft_start)
    #             logging.info(f"Obstacle length: {dlugosc_przeszkody}")
    #             sumaryczna_dlugosc_przeszkod += dlugosc_przeszkody
    #             left_turn() # powrot na srodek sciezki
    #             while szerokosc_przeszkody_powrot<=szerokosc_przeszkody:
    #                 encoder_tick=(left_ticks+right_ticks)/2
    #                 szerokosc_przeszkody_powrot=(encoder_tick/15)*math.pi*0.102
    #                 soft_start=forward(soft_start)
    #             right_turn()
    #             logging.info(f"Obstacle avoided.")
    #     ##DRIVING WHEN THERE ARE NO OBSTACLES##
    #     else:
        distance_tmp = alley_drive(distance_tmp, sumaryczna_dlugosc_przeszkod)
        if distance_tmp>=next_measure_pos and is_measure==True:
                next_measure_pos, soft_start = alley_measure(distance_tmp, dist_beetween_measures, next_measure_pos, soft_start)
                    
def curve(route : str, shelf_width : float,alley_width:float):
    mqtt_pub.publish(client, "mqtt/reset_encoders", "1")
    if route=='P':
        left_turn()
        alley(shelf_width+alley_width, 1, False)
        alley_end()
        left_turn()
        return 'L'
    elif route=='L':
        right_turn()
        alley(shelf_width+alley_width, 1, False)
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
            alley_width=float(input("Podaj szerokość alejki w [m]: "))
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
    logging.info(f"User data: length of alley - {length_of_alley}, shelf width - {shelf_width}, number of shelfs - {number_of_shelfs}, route - {route}, distance beetween measures - {dist_beetween_measures}, alley width  - {alley_width}")
    return length_of_alley, shelf_width, number_of_shelfs, route, dist_beetween_measures, alley_width

if __name__ == '__main__':
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    ser.reset_input_buffer()
    logging.info("====================")
    logging.info('-----New sesion-----')
    logging.info("====================")  
    client = mqtt_client.Client()
    client.on_connect=on_connect
    client.on_message=on_message
    client.connect("localhost", 1883)
    client.loop_start()
    length_of_alley, shelf_width, number_of_shelfs, route, dist_beetween_measures, alley_width = user_input()
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
                    route=curve(route,shelf_width,alley_width) 
        except KeyboardInterrupt:
            stop()
            logging.info('-----Manual exit-----')
            exit()
    stop() 
    distance_tmp=0