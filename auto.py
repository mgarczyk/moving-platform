import time
import serial
import json
import logging
import periphery
import paho.mqtt.client as mqtt_client

# CONFIG #
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
        MEASURE_HEIGHT = config["MEASURE_HEIGHT"]
        MEASURE_TIME = config["MEASURE_TIME"]
        LIDAR_FORWARD_AVOIDING_DISTANCE = config["LIDAR_FORWARD_TRANSFORM"] + config["LIDAR_FORWARD_REACTION"]
        LIDAR_LEFT_AVOIDING_DISTANCE = config["LIDAR_LEFT_TRANSFORM"] + config["LIDAR_LEFT_REACTION"]
        LIDAR_RIGHT_AVOIDING_DISTANCE = config["LIDAR_RIGHT_TRANSFORM"] + config["LIDAR_RIGHT_REACTION"]
        LIDAR_BACK_AVOIDING_DISTANCE = config["LIDAR_BACK_TRANSFORM"] + config["LIDAR_BACK_REACTION"]
        SET_PWM_LIFT = periphery.GPIO(config["SET_PWM_LIFT"], "out")
        DIR_LIFT = periphery.GPIO(config["DIR_LIFT"], "out")
        BROKER = config["MQTT_BROKER"]
        PORT = config["MQTT_PORT"]
        arduino = serial.Serial(config["ARDUINO_PORT"], 115200)
        arduino.reset_input_buffer()
        distance_tmp = 0
        liftlevel=0
        distance_tmp_before_obstacle = 0
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
    return LIDAR_forw_dist, LIDAR_right_dist, LIDAR_left_dist, LIDAR_back_dist, LIDAR_front_left, LIDAR_front_right


def prepare_us100_data(payload):
    text = str(payload)
    text = text[3:-2]
    distances = text.split(',')
    distances = [int(actual_shelf) for actual_shelf in distances]
    US_100_dist = distances[0:4]
    return US_100_dist


def on_message(client: mqtt_client, obj, msg):
    global LIDAR_forw_dist, LIDAR_right_dist, LIDAR_left_dist, LIDAR_back_dist,LIDAR_front_left, LIDAR_front_right, US_100_dist, liftlevel
    if msg.topic == "mqtt/liftlevel":
        liftlevel = int(msg.payload.decode('utf8'))
        print(liftlevel)
    elif msg.topic == "mqtt/lidar":
        LIDAR_forw_dist, LIDAR_right_dist, LIDAR_left_dist, LIDAR_back_dist, LIDAR_front_left, LIDAR_front_right = prepare_lidar_data(
            msg.payload)

def reset_encoders():                             
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

def stop_lift():
    SET_PWM_LIFT.write(False)

def lower():
    DIR_LIFT.write(False)
    SET_PWM_LIFT.write(True)


def stop():
    arduino.write(b"stop\n")
    reset_encoders()
    
def stop_measure():
    arduino.write(b"stop\n")

def encoder_distance():
    arduino.reset_input_buffer()
    distance_tmp = arduino.readline().decode('utf-8').rstrip()
    print(distance_tmp)
    distance_tmp = float(distance_tmp)
    return distance_tmp

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

def alley_init():
    reset_encoders()
    time.sleep(0.1)
    global distance_tmp
    distance_tmp = 0
    next_measure_pos = DIST_BEETWEEN_MEASURES
    sum_len_of_obstacles = 0
    time.sleep(0.5)
    forward()
    return distance_tmp, next_measure_pos, sum_len_of_obstacles

def alley_measure(distance_tmp: float, DIST_BEETWEEN_MEASURES: float, next_measure_pos: float):
    global liftlevel
    logging.info(f"Mesure distance: {distance_tmp}")
    stop_measure()
    lift()
    while True:
        if liftlevel>=MEASURE_HEIGHT:
            stop_lift()
            break
    time.sleep(MEASURE_TIME)
    lower()
    time.sleep(2)
    next_measure_pos += DIST_BEETWEEN_MEASURES
    forward()
    return next_measure_pos

def alley_end():
    stop()
    time.sleep(0.5)

def alley(distance_to_travel: float, DIST_BEETWEEN_MEASURES: float, is_measure: bool):
    distance_tmp, next_measure_pos, sum_len_of_obstacles = alley_init()
    global distance_tmp_before_obstacle
    while distance_tmp < distance_to_travel:
        # AVOIDING THE OBSTACLE#
        if any(i < LIDAR_FORWARD_AVOIDING_DISTANCE for i in LIDAR_forw_dist):
            obstacle_width = 0
            obstacle_width_return = 0
            obstacle_len = 0
            distance_tmp_before_obstacle = distance_tmp
            stop()
            time.sleep(1)
            if any(dist < LIDAR_FORWARD_AVOIDING_DISTANCE for dist in LIDAR_front_right):
                logging.info(f"Avoiding obstacle from right side.")
                left_turn()  # skret w lewo po wykryciu przeszkody
                time.sleep(1)
                reset_encoders()
                print(1)
                time.sleep(1)
                forward()  # jazda prosto do konca przeszkody - wolnego miejsca po prawej
                while any(i < LIDAR_RIGHT_AVOIDING_DISTANCE for i in LIDAR_right_dist):
                    if any(i < LIDAR_FORWARD_AVOIDING_DISTANCE for i in LIDAR_forw_dist):
                        logging.info("Can't avoid STOP.")
                        stop()
                        exit()
                    # droga pokonana na szerokosc
                    obstacle_width = encoder_distance()
                    logging.info(f"Avoiding: {min(LIDAR_right_dist)}")
                    time.sleep(0.01)
                logging.info(f"Obstacle width: {obstacle_width}")
                stop()
                time.sleep(1)
                right_turn()  # koniec przeszkody
                time.sleep(1)
                reset_encoders()
                time.sleep(1)
                forward()
                time.sleep(2)
                while any(i < LIDAR_RIGHT_AVOIDING_DISTANCE for i in LIDAR_right_dist):  # jazda na długosc
                    if any(i < LIDAR_FORWARD_AVOIDING_DISTANCE for i in LIDAR_forw_dist):
                        logging.error("Can't avoid STOP.")
                        stop()
                        exit()
                    obstacle_len=encoder_distance()
                sum_len_of_obstacles += obstacle_len
                logging.info(f"Obstacle length: {obstacle_len}")
                stop()
                time.sleep(1)
                right_turn()  # powrot na srodek sciezki
                time.sleep(1)
                reset_encoders()
                time.sleep(1)
                forward()
                while obstacle_width_return <= obstacle_width:
                    obstacle_width_return = encoder_distance()
                stop()
                time.sleep(1)
                left_turn()
                time.sleep(1)
                reset_encoders()
                time.sleep(1)
                forward()
                logging.info(f"Obstacle avoided.")
            elif any(dist < LIDAR_FORWARD_AVOIDING_DISTANCE for dist in LIDAR_front_left):
                logging.warning(f"Avoiding obstacle from left side.")
                right_turn()
                time.sleep(1)
                reset_encoders()
                # jazda prosto do konca przeszkody - wolnego miejsca po prawej
                forward()
                while any(i < LIDAR_LEFT_AVOIDING_DISTANCE for i in LIDAR_left_dist):
                    if any(i < LIDAR_FORWARD_AVOIDING_DISTANCE for i in LIDAR_forw_dist):
                        logging.error("Can't avoid STOP.")
                        stop()
                        exit()
                    # droga pokonana na szerokosc
                    obstacle_width = encoder_distance()
                logging.info(f"Obstacle width: {obstacle_width}")
                stop()
                time.sleep(1)
                left_turn()  # koniec przeszkody
                time.sleep(1)
                reset_encoders()
                forward()   
                time.sleep(2.5) # po tym czasie przeszkoda  będzie w polu widzenia lidaru
                while any(i < LIDAR_LEFT_AVOIDING_DISTANCE for i in LIDAR_left_dist):  # jazda na długosc
                    print(LIDAR_forw_dist)
                    if any(i < LIDAR_FORWARD_AVOIDING_DISTANCE for i in LIDAR_forw_dist):
                        logging.error("Can't avoid STOP.")
                        stop()
                        exit()
                    obstacle_len = encoder_distance()
                logging.info(f"Obstacle length: {obstacle_len}")
                sum_len_of_obstacles += obstacle_len
                stop()
                time.sleep(1)
                left_turn()  # powrot na srodek sciezki    
                time.sleep(1)
                reset_encoders()
                forward()
                while obstacle_width_return <= obstacle_width:
                    obstacle_width_return = encoder_distance()
                stop()
                time.sleep(1)
                right_turn()
                time.sleep(1)
                reset_encoders()
                forward()
                logging.info(f"Obstacle avoided.")
        # DRIVING WHEN THERE ARE NO OBSTACLES#
        else:
            distance_tmp = distance_tmp_before_obstacle + sum_len_of_obstacles + encoder_distance()
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
        except KeyboardInterrupt:
            logging.info('-----Manual exit-----')
            stop()
            config_f.close()
            exit()
    stop()
    config_f.close()
    exit()