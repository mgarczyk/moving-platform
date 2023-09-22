from periphery import GPIO
import adafruit_us100
import mqtt_pub
import time
import serial
import os
import json 

try:
    with open ("config.json") as config_f:
        config = json.load(config_f)
        UART_MUX = config["MUX_UART"]
        MUX_GPIO_A=GPIO(config["MUX_PIN_A"],"out")
        MUX_GPIO_B=GPIO(config["MUX_PIN_B"],"out")
        BROKER = config["MQTT_BROKER"]
        PORT = config["MQTT_PORT"]
        config_f.close()
except FileNotFoundError:
    print("Brak pliku konfiguracyjnego.")
    exit()

def Sensors(VAR_A,VAR_B):     
    UART_US100=serial.Serial(UART_MUX ,baudrate=9600)
    MUX_GPIO_A.write(VAR_A)
    MUX_GPIO_B.write(VAR_B)
    time.sleep(0.001)    
    us100=adafruit_us100.US100(UART_US100)
    distance=us100.distance
    if distance == None:
        distance=9999
    print(distance)
    return(distance)

def publisher_us100():
    client_id = "us_100"
    topic = "mqtt/us_100"
    client = mqtt_pub.connect_mqtt(client_id, BROKER, PORT)
    while True:
        try:
            x1=int(Sensors(False,True))
            x2=int(Sensors(True,False))
            x3=int(Sensors(False,False))
            x4=int(Sensors(True,True))
            mess=[x1,x2,x3,x4]
            distances=f"{mess}"
            print(distances)
            mqtt_pub.publish(client, topic, distances)
        except KeyboardInterrupt:
            MUX_GPIO_A.write(False)
            MUX_GPIO_B.write(False)
            break

if __name__ == "__main__":
    publisher_us100()
