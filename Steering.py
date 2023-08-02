import time
import periphery
import paho.mqtt.client as mqtt

pwm_R = periphery.PWM(0, 0)
pwm_L = periphery.PWM(1, 0)
Dir_L_GPIO=periphery.GPIO(71,"out")
Dir_R_GPIO=periphery.GPIO(72,"out")
pwm_R.frequency=1e3
pwm_L.frequency=1e3
data = -1


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("mqtt/steering",qos=1)

def on_message(client, userdata, msg):
    global data
    data = msg.payload.decode('utf8')

def pwm_set():
    pwm_R.duty_cycle = 0.25
    pwm_L.duty_cycle = 0.25
    pwm_L.enable()
    pwm_R.enable()


def forward():
    Dir_L_GPIO.write(True)
    Dir_R_GPIO.write(False)
    pwm_set()

def back():
    Dir_L_GPIO.write(False)
    Dir_R_GPIO.write(True)
    pwm_set()

def left():
    Dir_L_GPIO.write(False)
    Dir_R_GPIO.write(False)
    pwm_set()

def right():
    Dir_L_GPIO.write(True)
    Dir_R_GPIO.write(True)
    pwm_set()

def stop():
    pwm_R.duty_cycle = 1.0
    pwm_L.duty_cycle = 1.0
    pwm_L.enable()
    pwm_R.enable()
 

if __name__ == '__main__':
    client = mqtt.Client()
    client.on_connect = on_connect
    client.connect("localhost", 1883, 60)
  
    while True:
        client.on_message = on_message
        client.loop_start()
        while data=="Forward":
            print(data)
            forward()
        while data=="Back":
            print(data)
            back()
        while data=="Left":
            print(data)
            left()
        while data=="Right":
            print(data)
            right()
        else:
            print(data)
            stop()
