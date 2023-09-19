import time
import periphery
import paho.mqtt.client as mqtt
import os

PWM_motor = periphery.PWM(0, 0)
Dir_L_GPIO=periphery.GPIO(71,"out")
Dir_R_GPIO=periphery.GPIO(72,"out")
Dir_LIFT_GPIO=periphery.GPIO(157,"out")
PWM_LIFT_GPIO=periphery.GPIO(42,"out")
soft_start=True
lift_flag=True
PWM_motor.enable()
data = -1
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("mqtt/steering",qos=1)

def on_message(client, userdata, msg):
    global data
    data = msg.payload.decode('utf8')
    
def pwm_set_turn():
       PWM_motor.duty_cycle = 0.5

def pwm_set(soft_start):
    if soft_start == True:
        for speed in [0.75,0.7,0.65,0.6,0.55,0.5,0.45,0.4,0.35,0.3,0.25]:
            PWM_motor.duty_cycle = speed
            time.sleep(0.07)
    else:
        PWM_motor.duty_cycle = 0.25
    soft_start=False
    return soft_start

def forward(soft_start):
    Dir_L_GPIO.write(False)
    Dir_R_GPIO.write(False)
    soft_start=pwm_set(soft_start)
    return soft_start

def back(soft_start):
    Dir_L_GPIO.write(True)
    Dir_R_GPIO.write(True)
    soft_start=pwm_set(soft_start)
    return soft_start

def left():
    Dir_L_GPIO.write(False)
    Dir_R_GPIO.write(True)
    pwm_set_turn()

def right():
    Dir_L_GPIO.write(True)
    Dir_R_GPIO.write(False)
    pwm_set_turn()

def stop():
    PWM_motor.duty_cycle = 1.0
    PWM_LIFT_GPIO.write(False)
  
    
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
            lift_flag=False
            soft_start=forward(soft_start)
        while data=="Back":
            lift_flag=False
            soft_start=back(soft_start)
        while data=="Left":
            lift_flag=False
            soft_start=True
            left()
        while data=="Right":
            lift_flag=False
            soft_start=True
            right()
        while data=="Lower":
            if lift_flag==True:
                lower()
        while data=="Lift":
            if lift_flag==True: 
                lift()
        else:
            soft_start=True
            lift_flag=True
            stop()
        time.sleep(0.25)
