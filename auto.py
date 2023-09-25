import time
import serial
import math
import json
import logging
import periphery
import paho.mqtt.client as mqtt_client
import mqtt_pub

#CONFIG#
try:
    with open("config.json") as config_f:
        config = json.load(config_f)
        LIDAR_FORWARD_AVOIDING_DISTANCE = config["LIDAR_FORWARD_TRANSFORM"] + config["LIDAR_FORWARD_REACTION"]
        LIDAR_LEFT_AVOIDING_DISTANCE = config["LIDAR_LEFT_TRANSFORM"] + config["LIDAR_LEFT_REACTION"]
        LIDAR_RIGHT_AVOIDING_DISTANCE = config["LIDAR_RIGHT_TRANSFORM"] + config["LIDAR_RIGHT_REACTION"]
        LIDAR_BACK_AVOIDING_DISTANCE = config["LIDAR_BACK_TRANSFORM"] + config["LIDAR_BACK_REACTION"]
        SET_PWM_LIFT = periphery.GPIO(config["SET_PWM_LIFT"], "out")
        DIR_LIFT = periphery.GPIO(config["DIR_LIFT"], "out")
        US_100_REACTION = config["US_100_REACTION"]
        WHEEL_DIAMETER = config["WHEEL_DIAMETER"]
        BROKER = config["MQTT_BROKER"]
        PORT = config["MQTT_PORT"]
        arduino = serial.Serial(config["ARDUINO_PORT"], 9600, timeout=1)
        arduino.reset_input_buffer()
        distance_tmp = 0
        left_ticks = 0
        right_ticks = 0
        LIDAR_forw_dist = []
        LIDAR_right_dist = []
        LIDAR_left_dist = []
        LIDAR_back_dist = []
        US_100_dist = []
except FileNotFoundError:
    print("Brak pliku konfiguracyjnego.")
    exit()


# LOGGER CONFIG#
FORMAT = '%(asctime)s - %(message)s'
logging.basicConfig(filename='auto_logger.log', filemode='w',
                    level=logging.DEBUG, format=FORMAT)


def on_connect(client: mqtt_client, userdata, flags, rc):
    logging.info(f"Connected to broker with result code: {str(rc)}")
    client.subscribe([("mqtt/left_ticks", 1), ("mqtt/right_ticks",
                     1), ("mqtt/lidar", 0), ("mqtt/US_100_dist", 0)])


def remove_zeroes_LIDAR(vector: list):
    for elements in vector:
        try:
            vector.remove(0)
        except:
            break
    return vector


def prepare_lidar_data(payload):
    text = str(payload)
    text = text[3:-2]
    distances = text.split(',')
    distances = [int(actual_shelf) for actual_shelf in distances]
    LIDAR_forw_dist = distances[170:190]
    LIDAR_right_dist = distances[250:290]
    LIDAR_left_dist = distances[60:120]
    LIDAR_back_dist = distances[329:359]
    LIDAR_back_dist.extend(distances[0:30])
    remove_zeroes_LIDAR(LIDAR_forw_dist)
    remove_zeroes_LIDAR(LIDAR_right_dist)
    remove_zeroes_LIDAR(LIDAR_left_dist)
    remove_zeroes_LIDAR(LIDAR_back_dist)
    return LIDAR_forw_dist, LIDAR_right_dist, LIDAR_left_dist, LIDAR_back_dist


def prepare_us100_data(payload):
    text = str(payload)
    text = text[3:-2]
    distances = text.split(',')
    distances = [int(actual_shelf) for actual_shelf in distances]
    US_100_dist = distances[0:4]
    return US_100_dist


def on_message(client: mqtt_client, obj, msg):
    global left_ticks, right_ticks, LIDAR_forw_dist, LIDAR_right_dist, LIDAR_left_dist, LIDAR_back_dist, US_100_dist
    if msg.topic == "mqtt/left_ticks":
        left_ticks = int(msg.payload.decode('utf8'))
    elif msg.topic == "mqtt/right_ticks":
        right_ticks = int(msg.payload.decode('utf8'))
    elif msg.topic == "mqtt/lidar":
        LIDAR_forw_dist, LIDAR_right_dist, LIDAR_left_dist, LIDAR_back_dist = prepare_lidar_data(
            msg.payload)
        print(LIDAR_forw_dist)
    elif msg.topic == "mqtt/US_100_dist":
        US_100_dist = prepare_us100_data(msg.payload)


def forward():
    arduino.write(b"forward\n")


def back():
    arduino.write(b"back\n")


def left():
    arduino.write(b"left\n")


def right():
    arduino.write(b"right\n")


def lift():
    DIR_LIFT.write(True)
    SET_PWM_LIFT.write(True)


def lower():
    DIR_LIFT.write(False)
    SET_PWM_LIFT.write(True)


def stop():
    arduino.write(b"stop\n")


def left_turn():
    left()
    time.sleep(4)
    stop()
    mqtt_pub.publish(client, "mqtt/reset_encoders", "1")
    time.sleep(0.1)


def right_turn():
    right()
    time.sleep(4)
    stop()
    mqtt_pub.publish(client, "mqtt/reset_encoders", "1")
    time.sleep(0.1)


def alley_init(dist_beetwen_measures: float):
    mqtt_pub.publish(client, "mqtt/reset_encoders", "1")
    time.sleep(0.1)
    global distance_tmp
    distance_tmp = 0
    next_measure_pos = dist_beetween_measures
    sum_len_of_obstacle = 0
    forward()
    return distance_tmp, next_measure_pos, sum_len_of_obstacle


def alley_drive(distance_tmp: float, sum_len_of_obstacle: float):
    encoder_tick = (left_ticks+right_ticks)/2
    distance_tmp = sum_len_of_obstacle + (encoder_tick/14.85) * math.pi * WHEEL_DIAMETER
    print(distance_tmp)
    return distance_tmp


def alley_measure(distance_tmp: float, dist_beetween_measures: float, next_measure_pos: float):
    logging.info(f"Mesure distance: {distance_tmp}")
    stop()
    lift()
    time.sleep(2)
    lower()
    time.sleep(2)
    next_measure_pos += dist_beetween_measures
    forward()
    return next_measure_pos


def alley_end():
    stop()
    time.sleep(0.5)


def alley(distance_to_travel: float, dist_beetween_measures: float, is_measure: bool):
    distance_tmp, next_measure_pos, sum_len_of_obstacle = alley_init(dist_beetween_measures)
    while distance_tmp < distance_to_travel:
        #AVOIDING THE OBSTACLE#
        if any(i < LIDAR_FORWARD_AVOIDING_DISTANCE for i in LIDAR_forw_dist) or any(i < US_100_REACTION for i in US_100_dist):
            obstacle_width = 0
            obstacle_width_return = 0
            obstacle_len = 0
            if US_100_dist[2] < US_100_REACTION or US_100_dist[3] < US_100_REACTION:
                logging.info(f"Avoiding obstacle from right side.")
                left_turn()  # skret w lewo po wykryciu przeszkody
                # jazda prosto do konca przeszkody - wolnego miejsca po prawej
                while any(i < LIDAR_RIGHT_AVOIDING_DISTANCE for i in LIDAR_right_dist):
                    if any(i < US_100_REACTION for i in US_100_dist):
                        logging.info("Can't avoid STOP.")
                        stop()
                        exit()
                    encoder_tick = (left_ticks+right_ticks)/2
                    # droga pokonana na szerokosc
                    obstacle_width = (encoder_tick/15) * math.pi * WHEEL_DIAMETER
                    forward()  # jazda do przodu do momentu spelnienia warunku
                logging.info(f"Obstacle width: {obstacle_width}")
                right_turn()  # koniec przeszkody
                while any(i < LIDAR_RIGHT_AVOIDING_DISTANCE for i in LIDAR_right_dist): # jazda na długosc
                    if any(i < US_100_REACTION for i in US_100_dist):
                        logging.error("Can't avoid STOP.")
                        stop()
                        exit()
                    encoder_tick = (left_ticks+right_ticks)/2
                    obstacle_len = (encoder_tick/15) * math.pi * WHEEL_DIAMETER
                    forward()
                sum_len_of_obstacle += obstacle_len
                logging.info(f"Obstacle length: {obstacle_len}")
                right_turn()  # powrot na srodek sciezki
                while obstacle_width_return <= obstacle_width:
                    encoder_tick = (left_ticks+right_ticks)/2
                    obstacle_width_return = (encoder_tick/15) * math.pi * WHEEL_DIAMETER
                    forward()
                left_turn()
                logging.info(f"Obstacle avoided.")
            else:
                logging.warning(f"Avoiding obstacle from left side.")
                right_turn()
                # jazda prosto do konca przeszkody - wolnego miejsca po prawej
                while any(i < LIDAR_LEFT_AVOIDING_DISTANCE for i in LIDAR_left_dist):
                    if any(i < US_100_REACTION for i in US_100_dist):
                        logging.error("Can't avoid STOP.")
                        stop()
                        exit()
                    encoder_tick = (left_ticks+right_ticks)/2
                    # droga pokonana na szerokosc
                    obstacle_width = (encoder_tick/15) * math.pi * WHEEL_DIAMETER
                    forward()  # jazda do przodu do momentu spelnienia warunku
                logging.info(f"Obstacle width: {obstacle_width}")
                left_turn()  # koniec przeszkody
                while any(i < LIDAR_LEFT_AVOIDING_DISTANCE for i in LIDAR_left_dist):  # jazda na długosc
                    # print(LIDAR_forw_dist)
                    if any(i < US_100_REACTION for i in US_100_dist):
                        logging.error("Can't avoid STOP.")
                        stop()
                        exit()
                    encoder_tick = (left_ticks+right_ticks)/2
                    obstacle_len = (encoder_tick/15) * math.pi * WHEEL_DIAMETER
                    forward()
                logging.info(f"Obstacle length: {obstacle_len}")
                sum_len_of_obstacle += obstacle_len
                left_turn()  # powrot na srodek sciezki
                while obstacle_width_return <= obstacle_width:
                    encoder_tick = (left_ticks+right_ticks)/2
                    obstacle_width_return = (encoder_tick/15) * math.pi * WHEEL_DIAMETER
                    forward()
                right_turn()
                logging.info(f"Obstacle avoided.")
        #DRIVING WHEN THERE ARE NO OBSTACLES#
        else:
            distance_tmp = alley_drive(
                distance_tmp, sum_len_of_obstacle)
            if distance_tmp >= next_measure_pos and is_measure == True:
                next_measure_pos = alley_measure(
                    distance_tmp, dist_beetween_measures, next_measure_pos)


def curve(route: str, shelf_width: float, alley_width: float):
    mqtt_pub.publish(client, "mqtt/reset_encoders", "1")
    if route == 'P':
        left_turn()
        alley(shelf_width+alley_width, 1, False)
        alley_end()
        left_turn()
        return 'L'
    elif route == 'L':
        right_turn()
        alley(shelf_width+alley_width, 1, False)
        alley_end()
        right_turn()
        return 'P'


def user_input():
    while True:
        try:
            length_of_alley = float(input("Podaj długość magazynu w [m]: "))
            break
        except ValueError:
            print("Podaj ponownie")
    while True:
        try:
            alley_width = float(input("Podaj szerokość alejki w [m]: "))
            break
        except ValueError:
            print("Podaj ponownie")
    while True:
        try:
            shelf_width = float(input("Podaj szerokość regału w [m]: "))
            break
        except ValueError:
            print("Podaj ponownie")
    while True:
        try:
            dist_beetween_measures = float(
                input("Podaj dystans między pomiarami: "))
            break
        except ValueError:
            print("Podaj ponownie")
    while True:
        try:
            number_of_shelfs = int(input("Podaj ilośc regałów: "))
            break
        except ValueError:
            print("Podaj ponownie")
    while True:
        try:
            route = input("Podaj po której stronie robota jest ściana (L / P)")
            if route in ['L', 'P']:
                break
            raise ValueError
        except ValueError:
            print("Podaj ponownie.")
    logging.info(
        f"User data: length of alley - {length_of_alley}, shelf width - {shelf_width}, number of shelfs - {number_of_shelfs}, route - {route}, distance beetween measures - {dist_beetween_measures}, alley width  - {alley_width}")
    return length_of_alley, shelf_width, number_of_shelfs, route, dist_beetween_measures, alley_width


if __name__ == '__main__':
    logging.info("====================")
    logging.info('-----New sesion-----')
    logging.info("====================")
    client = mqtt_client.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT)
    client.loop_start()
    length_of_alley, shelf_width, number_of_shelfs, route, dist_beetween_measures, alley_width = user_input()
    actual_shelf = 0
    while actual_shelf <= number_of_shelfs:
        try:
            mqtt_pub.publish(client, "mqtt/reset_encoders", "1")
            time.sleep(0.3)
            lift_flag = True
            alley(length_of_alley, dist_beetween_measures, lift_flag)
            actual_shelf = actual_shelf+1
            if actual_shelf <= number_of_shelfs:
                route = curve(route, shelf_width, alley_width)
            stop()
            config_f.close()
            exit()
        except KeyboardInterrupt:
            logging.info('-----Manual exit-----')
            stop()
            config_f.close()
            exit()
    stop()
