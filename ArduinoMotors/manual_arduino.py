import time
import periphery
import paho.mqtt.client as mqtt
import serial

Dir_LIFT_GPIO = periphery.GPIO(157, "out")
PWM_LIFT_GPIO = periphery.GPIO(42, "out")
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
    Dir_LIFT_GPIO.write(True)
    PWM_LIFT_GPIO.write(True)


def lower():
    stop()
    Dir_LIFT_GPIO.write(False)
    PWM_LIFT_GPIO.write(True)


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
    arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    arduino.reset_input_buffer()
    client = mqtt.Client()
    client.on_connect = on_connect
    client.connect("localhost", 1883)
    data_before = ""
    try:
        while True:
            client.on_message = on_message
            client.loop_start()
            if data_actual != data_before:
                choose_direction(data_actual)
            data_before = data_actual
            time.sleep(0.25)
    except KeyboardInterrupt:
        stop()
        exit()
