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
topic = "mqtt/liftlevel"
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
            height=height_return(tfmini)
            mqtt_pub.publish(client, topic, f'Height: {height}')
        except KeyboardInterrupt:
            print("Sensor Error")
            break

if __name__=="__main__":
    publisher_height()


