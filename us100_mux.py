from periphery import GPIO
import adafruit_us100
import mqtt_pub
import time
import serial

##MUX PINOUT##
MUX_PIN_A=71
MUX_PIN_B=72
MUX_GPIO_A=GPIO(MUX_PIN_A,"out")
MUX_GPIO_B=GPIO(MUX_PIN_B,"out")

##BROKER##
broker = 'localhost'
port = 1883
topic = "/home/radxa/moving_platform/mqtt/distance"
client_id = f'publish-distance'

def Sensors(VAR_A,VAR_B):     
    UART_US100=serial.Serial("/dev/ttyS4",baudrate=9600,timeout=1)
    MUX_GPIO_A.write(VAR_A)
    MUX_GPIO_B.write(VAR_B)
    time.sleep(0.5)    
    us100= adafruit_us100.US100(UART_US100)
    distance=us100.distance
    return(distance)

def publisher_us100():
    client = mqtt_pub.connect_mqtt(client_id, broker, port)
    while True:
        try:
            x1=Sensors(False,False)
            mqtt_pub.publish(client, topic, f'x1: {x1}')
            time.sleep(0.1)
            x2=Sensors(False,True)
            mqtt_pub.publish(client, topic, f'x2: {x2}')
            time.sleep(0.1)
            x3=Sensors(True,False)
            mqtt_pub.publish(client, topic, f'x3: {x3}')
            time.sleep(0.1)
            x4=Sensors(True,True)
            mqtt_pub.publish(client, topic, f'x4: {x4}')
            time.sleep(0.1)
        except KeyboardInterrupt:
            MUX_GPIO_A.write(False)
            MUX_GPIO_B.write(False)
            break

if __name__ == "__main__":
    publisher_us100()
