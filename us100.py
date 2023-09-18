from periphery import GPIO
import adafruit_us100
import mqtt_pub
import time
import serial
import os

##MUX PINOUT##
MUX_PIN_A=154
MUX_PIN_B=156
MUX_GPIO_A=GPIO(MUX_PIN_A,"out")
MUX_GPIO_B=GPIO(MUX_PIN_B,"out")

##BROKER##
broker = 'localhost'
port = 1883
topic = "mqtt/distance"
client_id = f'publish-distance'

def Sensors(VAR_A,VAR_B):     
    UART_US100=serial.Serial("/dev/ttyS4",baudrate=9600)
    MUX_GPIO_A.write(VAR_A)
    MUX_GPIO_B.write(VAR_B)
    time.sleep(0.001)    
    us100=adafruit_us100.US100(UART_US100)
    distance=us100.distance
    if distance == None:
        distance=9999
    # print(distance)
    return(distance)

def publisher_us100():
    client = mqtt_pub.connect_mqtt(client_id, broker, port)
    while True:
        try:
            x1=int(Sensors(False,True))
            x2=int(Sensors(True,False))
            x3=int(Sensors(False,False))
            x4=int(Sensors(True,True))
            mess=[x1,x2,x3,x4]
            distances=f"{mess}"
            mqtt_pub.publish(client, topic, distances)
        except KeyboardInterrupt:
            MUX_GPIO_A.write(False)
            MUX_GPIO_B.write(False)
            break
if __name__ == "__main__":
    publisher_us100()
