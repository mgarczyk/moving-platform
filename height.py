import time
import adafruit_tfmini
import serial
import periphery
import adafruit_us100
import mqtt_pub

####Faktyczny skrypt####
##BROKER##
broker = 'localhost'
port = 1883
topic = "/mqtt/elevator_height"
client_id = f'publish-height'

uart = serial.Serial("/dev/ttyS2", timeout=1)
tfmini = adafruit_tfmini.TFmini(uart)

def height_return(tfmini):
    height=tfmini.distance+58
    return height

def publisher_height():
    client = mqtt_pub.connect_mqtt(client_id, broker, port)
    while True:
        try:
            height=height_return(uart,tfmini)
            mqtt_pub.publish(client, topic, f'Height: {height}')
        except KeyboardInterrupt:
            print("Sensor Error")
            break

if __name__=="__main__":
    publisher_height()

###Dodatkowe###
# def lift():
#     Dir_LIFT_GPIO.write(True)
#     PWM_LIFT_GPIO.write(True)

# def lower():
#     Dir_LIFT_GPIO.write(False)
#     PWM_LIFT_GPIO.write(True)

# def stop():
#     PWM_LIFT_GPIO.write(False)

# Dir_LIFT_GPIO=periphery.GPIO(157,"out")
# PWM_LIFT_GPIO=periphery.GPIO(42,"out")

# ##MUX PINOUT##
# MUX_PIN_A=154
# MUX_PIN_B=156
# MUX_GPIO_A=periphery.GPIO(MUX_PIN_A,"out")
# MUX_GPIO_B=periphery.GPIO(MUX_PIN_B,"out")

# def Sensors(VAR_A,VAR_B):     
#     UART_US100=serial.Serial("/dev/ttyS4",baudrate=9600)
#     MUX_GPIO_A.write(VAR_A)
#     MUX_GPIO_B.write(VAR_B)
#     time.sleep(0.001)    
#     us100=adafruit_us100.US100(UART_US100)
#     distance=us100.distance
#     return(distance)

# while True:
#     print(f'Height: {height_return(uart,tfmini)}')
#     print(f'Sensor 1: {Sensors(False,True)}')
#     print(f'Sensor 2: {Sensors(True,False)}')
#     print(f'Sensor 3: {Sensors(False,False)}')
#     print(f'Sensor 4: {Sensors(True,True)}')
#     time.sleep(1)

###---###

