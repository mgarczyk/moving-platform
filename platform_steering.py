import time
import periphery
import paho.mqtt.client as mqtt
import os

pwm_R = periphery.PWM(0, 0)
pwm_L = periphery.PWM(1, 0)
Dir_L_GPIO=periphery.GPIO(71,"out")
Dir_R_GPIO=periphery.GPIO(72,"out")
Dir_LIFT_GPIO=periphery.GPIO(157,"out")
PWM_LIFT_GPIO=periphery.GPIO(42,"out")

#pwm_R.frequency=1e3
#pwm_L.frequency=1e3
pwm_L.enable()
pwm_R.enable()
flag=True
data = -1

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("mqtt/steering",qos=1)

def on_message(client, userdata, msg):
    global data
    data = msg.payload.decode('utf8')
    
def pwm_set_turn():
       pwm_R.duty_cycle = 0.5
       pwm_L.duty_cycle = 0.5
       flag=False

def pwm_set():
    #if soft_start == True:
    #    pwm_R.duty_cycle = 0.75
    #    pwm_L.duty_cycle = 0.75
    #    time.sleep(0.25)
    #    pwm_R.duty_cycle = 0.5
    #    pwm_L.duty_cycle = 0.5
    #    time.sleep(0.25)
    #    soft_start=False
   # else:   
        pwm_R.duty_cycle = 0.25
        pwm_L.duty_cycle = 0.25
        flag=False

def forward():
    Dir_L_GPIO.write(False)
    Dir_R_GPIO.write(False)
    pwm_set()

def back():
    Dir_L_GPIO.write(True)
    Dir_R_GPIO.write(True)
    pwm_set()

def left():
    Dir_L_GPIO.write(False)
    Dir_R_GPIO.write(True)
    pwm_set_turn()

def right():
    Dir_L_GPIO.write(True)
    Dir_R_GPIO.write(False)
    pwm_set_turn()

def stop():
    pwm_R.duty_cycle = 1.0
    pwm_L.duty_cycle = 1.0
    PWM_LIFT_GPIO.write(False)
    flag=True
    
def lift():
    Dir_LIFT_GPIO.write(True)
    PWM_LIFT_GPIO.write(True)

def lower():
    Dir_LIFT_GPIO.write(False)
    PWM_LIFT_GPIO.write(True)

if __name__ == '__main__':
    client = mqtt.Client()
    client.on_connect = on_connect
    client.connect("localhost", 1883)

    while True:
        client.on_message = on_message
        client.loop_start()
        while data=="Forward":
            forward()
        while data=="Back":
            back()
        while data=="Left":
            left()
        while data=="Right":
            right()
        while data=="Lower":
            if flag==True:
                lower()
        while data=="Lift":
            if flag==True: 
                lift()
        else:
            stop()
            soft_start=True
        time.sleep(0.25)
