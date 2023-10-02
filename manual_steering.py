import time
import serial
import json
import periphery
import paho.mqtt.client as mqtt


try:
    with open ("config.json") as config_f:
        config = json.load(config_f)
        DIR_LIFT = periphery.GPIO(config["DIR_LIFT"], "out")
        SET_PWM_LIFT = periphery.GPIO(config["SET_PWM_LIFT"], "out")
        BROKER = config["MQTT_BROKER"]
        PORT = config["MQTT_PORT"]
        arduino = serial.Serial(config["ARDUINO_PORT"], 9600, timeout=1)
        arduino.reset_input_buffer()
        config_f.close()
except FileNotFoundError:
    print("Brak pliku konfiguracyjnego.")
    exit()

lift_flag = True
data_actual = "-1"


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("mqtt/steering", qos=1)


def on_message(client, userdata, msg):
    global data_actual
    data_actual = msg.payload.decode('utf8')


def forward():
    arduino.write(b"forward\n")


def back():
    arduino.write(b"back\n")


def left():
    arduino.write(b"left\n")


def right():
    arduino.write(b"right\n")


def stop():
    arduino.write(b"stop\n")


def lift():
    stop()
    DIR_LIFT.write(True)
    SET_PWM_LIFT.write(True)


def lower():
    stop()
    DIR_LIFT.write(False)
    SET_PWM_LIFT.write(True)


def choose_direction(data_actual: str):
    if data_actual == "Forward":
        forward()
    elif data_actual == "Back":
        back()
    elif data_actual == "Left":
        left()
    elif data_actual == "Right":
        right()
    elif data_actual == "Lower":
        lower()
    elif data_actual == "Lift":
        lift()
    else:
        stop()

if __name__ == '__main__':
    client = mqtt.Client()
    client.on_connect = on_connect
    client.connect(BROKER, PORT)
    data_before = ""
    try:
        while True:
            client.on_message = on_message
            client.loop_start()
            if data_actual != data_before:
                choose_direction(data_actual)
                print(data_actual)
            data_before = data_actual
            time.sleep(0.25)
    except KeyboardInterrupt:
        stop()
        exit()
