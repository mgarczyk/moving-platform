import time
import serial
import math
import json
import logging
import periphery
import paho.mqtt.client as mqtt_client
import mqtt_pub

# CONFIG#
try:
    with open("config.json") as config_f:
        config = json.load(config_f)
        DIST_BEETWEEN_MEASURES = config["DIST_BEETWEEN_MEASURES"]
        MEASURE_FLAG = config["MEASURE_FLAG"]
        NUMBER_OF_SHELFS = config["NUMBER_OF_SHELFS"]
        START_WALL_POS = config["START_WALL_POS"]
        SHELF_WIDTH = config["SHELF_WIDTH"]
        ALLEY_WIDTH = config["ALLEY_WIDTH"]
        ALLEY_LEN = config["ALLEY_LEN"]
        LIDAR_FORWARD_AVOIDING_DISTANCE = config["LIDAR_FORWARD_TRANSFORM"] + config["LIDAR_FORWARD_REACTION"]
        LIDAR_LEFT_AVOIDING_DISTANCE = config["LIDAR_LEFT_TRANSFORM"] + config["LIDAR_LEFT_REACTION"]
        LIDAR_RIGHT_AVOIDING_DISTANCE = config["LIDAR_RIGHT_TRANSFORM"] + config["LIDAR_RIGHT_REACTION"]
        LIDAR_BACK_AVOIDING_DISTANCE = config["LIDAR_BACK_TRANSFORM"] + config["LIDAR_BACK_REACTION"]
        SET_PWM_LIFT = periphery.GPIO(config["SET_PWM_LIFT"], "out")
        DIR_LIFT = periphery.GPIO(config["DIR_LIFT"], "out")
        LIDAR_FORWARD_AVOIDING_DISTANCE = config["LIDAR_FORWARD_AVOIDING_DISTANCE"]
        WHEEL_DIAMETER = config["WHEEL_DIAMETER"]
        BROKER = config["MQTT_BROKER"]
        PORT = config["MQTT_PORT"]
        arduino = serial.Serial(config["ARDUINO_PORT"], 9600, timeout=0.1)
        arduino.reset_input_buffer()
        distance_tmp = 0
        left_ticks = 0
        right_ticks = 0
        LIDAR_forw_dist = []
        LIDAR_right_dist = []
        LIDAR_left_dist = []
        LIDAR_back_dist = []
        US_100_dist = [999,999,999,999]
except FileNotFoundError:
    print("Brak pliku konfiguracyjnego.")
    exit()


# LOGGER CONFIG#
FORMAT = '%(asctime)s - %(message)s'
logging.basicConfig(filename='auto_logger.log', filemode='w',
                    level=logging.DEBUG, format=FORMAT)


def on_connect(client: mqtt_client, userdata, flags, rc):
    logging.info(f"Connected to broker with result code: {str(rc)}")
    client.subscribe([("mqtt/left_ticks", 1), ("mqtt/right_ticks",1), ("mqtt/lidar", 0), ("mqtt/us_100_dist", 0)])


def remove_zeroes_LIDAR(vector: list):
    vector = [i for i in vector if i != 0]
    return vector


def prepare_lidar_data(payload):
    text = str(payload)
    text = text[3:-2]
    distances = text.split(',')
    distances = [int(actual_shelf) for actual_shelf in distances]
    LIDAR_front_left=distances[160:180]
    LIDAR_front_left=remove_zeroes_LIDAR(LIDAR_front_left)
    LIDAR_front_right=distances[181:200]
    LIDAR_front_right=remove_zeroes_LIDAR(LIDAR_front_right)
    LIDAR_forw_dist = distances[155:215]
    LIDAR_forw_dist = remove_zeroes_LIDAR(LIDAR_forw_dist)
    LIDAR_right_dist = distances[245:305]
    LIDAR_right_dist = remove_zeroes_LIDAR(LIDAR_right_dist)
    LIDAR_left_dist = distances[50:110]
    LIDAR_left_dist = remove_zeroes_LIDAR(LIDAR_left_dist)
    LIDAR_back_dist = distances[329:359]
    LIDAR_back_dist.extend(distances[0:30])
    LIDAR_back_dist = remove_zeroes_LIDAR(LIDAR_back_dist)
    logging.info(f"update: {LIDAR_forw_dist}")
    return LIDAR_forw_dist, LIDAR_right_dist, LIDAR_left_dist, LIDAR_back_dist, LIDAR_front_left, LIDAR_front_right


def prepare_us100_data(payload):
    text = str(payload)
    text = text[3:-2]
    distances = text.split(',')
    distances = [int(actual_shelf) for actual_shelf in distances]
    US_100_dist = distances[0:4]
    return US_100_dist


def on_message(client: mqtt_client, obj, msg):
    global left_ticks, right_ticks, LIDAR_forw_dist, LIDAR_right_dist, LIDAR_left_dist, LIDAR_back_dist,LIDAR_front_left, LIDAR_front_right, US_100_dist
    if msg.topic == "mqtt/left_ticks":
        left_ticks = int(msg.payload.decode('utf8'))
    elif msg.topic == "mqtt/right_ticks":
        right_ticks = int(msg.payload.decode('utf8'))
    elif msg.topic == "mqtt/lidar":
        LIDAR_forw_dist, LIDAR_right_dist, LIDAR_left_dist, LIDAR_back_dist, LIDAR_front_left, LIDAR_front_right = prepare_lidar_data(
            msg.payload)
    # elif msg.topic == "mqtt/us_100_dist":
    #     try:
    #         US_100_dist = prepare_us100_data(msg.payload)
    #         i = US_100_dist[0]
        # except IndexError:
        #     pass

def reset_encoders():                               # <-------------------DO RESETOWANIA ENKODERÓW, CHYBA DODAŁEM WSZĘDZIE GDZIE MA BYĆ------------------------------>
    arduino.write(b"reset\n") 

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
    reset_encoders()

def encoder_status():
    arduino.write(b"status\n")
    time.sleep(0.01)
    encoder_tick=arduino.readline()
    return encoder_tick

def left_turn():
    left()
    time.sleep(2.75)
    stop()
    reset_encoders()
    time.sleep(0.1)


def right_turn():
    right()
    time.sleep(2.75)
    stop()
    reset_encoders()
    time.sleep(0.1)

def read_encoders():
    encoder = arduino.readline()
    print(encoder)

def alley_init():
    reset_encoders()
    time.sleep(0.1)
    global distance_tmp
    distance_tmp = 0
    next_measure_pos = DIST_BEETWEEN_MEASURES
    sum_len_of_obstacle = 0
    forward()
    return distance_tmp, next_measure_pos, sum_len_of_obstacle


def alley_drive(distance_tmp: float, sum_len_of_obstacle: float):
    # encoder_tick = (left_ticks+right_ticks)/2
    distance_tmp = sum_len_of_obstacle + (encoder_tick/14.85) * math.pi * WHEEL_DIAMETER
    print(distance_tmp)
    return distance_tmp


def alley_measure(distance_tmp: float, DIST_BEETWEEN_MEASURES: float, next_measure_pos: float):
    logging.info(f"Mesure distance: {distance_tmp}")
    stop()
    lift()
    time.sleep(2)
    lower()
    time.sleep(2)
    next_measure_pos += DIST_BEETWEEN_MEASURES
    forward()
    return next_measure_pos


def alley_end():
    stop()
    time.sleep(0.5)


def alley(distance_to_travel: float, DIST_BEETWEEN_MEASURES: float, is_measure: bool):
    distance_tmp, next_measure_pos, sum_len_of_obstacle = alley_init()
    while distance_tmp < distance_to_travel:
        # AVOIDING THE OBSTACLE#
        if any(i < LIDAR_FORWARD_AVOIDING_DISTANCE for i in LIDAR_forw_dist):
            obstacle_width = 0
            obstacle_width_return = 0
            obstacle_len = 0
            # logging.info(f"US_100: {US_100_dist}")
            if any(dist < LIDAR_FORWARD_AVOIDING_DISTANCE for dist in LIDAR_front_right):
                logging.info(f"Avoiding obstacle from right side.")
                left_turn()  # skret w lewo po wykryciu przeszkody
                forward()  # jazda prosto do konca przeszkody - wolnego miejsca po prawej
                while any(i < LIDAR_RIGHT_AVOIDING_DISTANCE for i in LIDAR_right_dist):
                    if any(i < LIDAR_FORWARD_AVOIDING_DISTANCE for i in LIDAR_forw_dist):
                        logging.info("Can't avoid STOP.")
                        stop()
                        exit()
                    # encoder_tick = (left_ticks+right_ticks)/2
                    # droga pokonana na szerokosc
                    obstacle_width = (encoder_tick/15) * math.pi * WHEEL_DIAMETER
                    logging.info(f"Avoiding: {min(LIDAR_right_dist)}")
                    time.sleep(0.01)
                logging.info(f"Obstacle width: {obstacle_width}")
                right_turn()  # koniec przeszkody
                forward()
                time.sleep(2.5)
                while any(i < LIDAR_RIGHT_AVOIDING_DISTANCE for i in LIDAR_right_dist):  # jazda na długosc
                    if any(i < LIDAR_FORWARD_AVOIDING_DISTANCE for i in LIDAR_forw_dist):
                        logging.error("Can't avoid STOP.")
                        stop()
                        exit()
                    # encoder_tick = (left_ticks+right_ticks)/2
                    obstacle_len = (encoder_tick/15) * math.pi * WHEEL_DIAMETER
                sum_len_of_obstacle += obstacle_len
                logging.info(f"Obstacle length: {obstacle_len}")
                right_turn()  # powrot na srodek sciezki
                forward()
                while obstacle_width_return <= obstacle_width:
                    # encoder_tick = (left_ticks+right_ticks)/2
                    obstacle_width_return = (encoder_tick/15) * math.pi * WHEEL_DIAMETER
                left_turn()
                forward()
                logging.info(f"Obstacle avoided.")
            elif any(dist < LIDAR_FORWARD_AVOIDING_DISTANCE for dist in LIDAR_front_left):
                logging.warning(f"Avoiding obstacle from left side.")
                right_turn()
                # jazda prosto do konca przeszkody - wolnego miejsca po prawej
                forward()
                while any(i < LIDAR_LEFT_AVOIDING_DISTANCE for i in LIDAR_left_dist):
                    if any(i < LIDAR_FORWARD_AVOIDING_DISTANCE for i in LIDAR_forw_dist):
                        logging.error("Can't avoid STOP.")
                        stop()
                        exit()
                    # encoder_tick = (left_ticks+right_ticks)/2
                    # droga pokonana na szerokosc
                    obstacle_width = (encoder_tick/15) * math.pi * WHEEL_DIAMETER
                logging.info(f"Obstacle width: {obstacle_width}")
                left_turn()  # koniec przeszkody
                forward()   
                time.sleep(2.5) # po tym czasie przeszkoda będzie w kącie wykrywania lidaru
                while any(i < LIDAR_LEFT_AVOIDING_DISTANCE for i in LIDAR_left_dist):  # jazda na długosc
                    print(LIDAR_forw_dist)
                    if any(i < LIDAR_FORWARD_AVOIDING_DISTANCE for i in LIDAR_forw_dist):
                        logging.error("Can't avoid STOP.")
                        stop()
                        exit()
                    # encoder_tick = (left_ticks+right_ticks)/2
                    obstacle_len = (encoder_tick/15) * math.pi * WHEEL_DIAMETER
                logging.info(f"Obstacle length: {obstacle_len}")
                sum_len_of_obstacle += obstacle_len
                left_turn()  # powrot na srodek sciezki
                forward()
                while obstacle_width_return <= obstacle_width:
                    # encoder_tick = (left_ticks+right_ticks)/2
                    obstacle_width_return = (encoder_tick/15) * math.pi * WHEEL_DIAMETER
                right_turn()
                logging.info(f"Obstacle avoided.")
        # DRIVING WHEN THERE ARE NO OBSTACLES#
        else:
            distance_tmp = alley_drive(distance_tmp, sum_len_of_obstacle)
            if distance_tmp >= next_measure_pos and is_measure == True:
                next_measure_pos = alley_measure(distance_tmp, DIST_BEETWEEN_MEASURES, next_measure_pos)


def curve(START_WALL_POS: str, SHELF_WIDTH: float, ALLEY_WIDTH: float):
    reset_encoders()
    if START_WALL_POS == 'P':
        left_turn()
        alley(SHELF_WIDTH+ALLEY_WIDTH, 1, MEASURE_FLAG)
        alley_end()
        left_turn()
        return 'L'
    elif START_WALL_POS == 'L':
        right_turn()
        alley(SHELF_WIDTH+ALLEY_WIDTH, 1, MEASURE_FLAG)
        alley_end()
        right_turn()
        return 'P'


if __name__ == '__main__':
    stop()
    logging.info("====================")
    logging.info('-----New sesion-----')
    logging.info("====================")
    client = mqtt_client.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT)
    client.loop_start()
    actual_shelf = 0
    while actual_shelf <= NUMBER_OF_SHELFS:
        try:
            reset_encoders()
            time.sleep(0.1)
            alley(ALLEY_LEN, DIST_BEETWEEN_MEASURES, MEASURE_FLAG)
            actual_shelf = actual_shelf+1
            if actual_shelf <= NUMBER_OF_SHELFS:
                START_WALL_POS = curve(START_WALL_POS, SHELF_WIDTH, ALLEY_WIDTH)
            stop()
            config_f.close()
            exit()
        except KeyboardInterrupt:
            logging.info('-----Manual exit-----')
            stop()
            config_f.close()
            exit()