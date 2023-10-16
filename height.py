import json
import serial
import adafruit_tfmini
import mqtt_pub
try:
    with open ("config.json") as config_f:
        config = json.load(config_f)
        BROKER = config["MQTT_BROKER"]
        PORT = config["MQTT_PORT"]
        LIFT_HEIGHT_CONSTANT = config["LIFT_HEIGHT_CONSTANT"]
        UART_TFMINI = serial.Serial(config["TFMINI_PORT"], timeout=1)     
        tfmini = adafruit_tfmini.TFmini(UART_TFMINI)
        config_f.close()
except FileNotFoundError:
    print("Brak pliku konfiguracyjnego.")
    exit()

def height_return(tfmini):
    height=tfmini.distance+LIFT_HEIGHT_CONSTANT
    return height

def publisher_height(topic : str, client_id : str):
    client = mqtt_pub.connect_mqtt(client_id, BROKER, PORT)
    while True:
        try:
            height=height_return(tfmini)
            mqtt_pub.publish(client, topic, height)
        except KeyboardInterrupt:
            print("Sensor Error")
            break

if __name__=="__main__":
    topic = "mqtt/liftlevel"
    client_id = f'publish-height'
    publisher_height(topic, client_id)


