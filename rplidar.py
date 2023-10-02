import json
import time
from math import floor
from adafruit_rplidar import RPLidar
from paho.mqtt import client as mqtt_client
import copy
import mqtt_pub

try:
    with open ("config.json") as config_f:
        config = json.load(config_f)
        LIDAR = RPLidar(None, config["LIDAR_PORT"], timeout=3)
        BROKER = config["MQTT_BROKER"]
        PORT = config["MQTT_PORT"]
        config_f.close()
except FileNotFoundError:
    print("Brak pliku konfiguracyjnego.")
    exit()

max_distance = 0
def connect_mqtt(client_id : str, broker : str, port : int ):
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client
     
def distances(scan_data):
    Front=scan_data[180]
    print(f'Front: {Front}')   
    Left=scan_data[90]
    print(f'Left: {Left}')
    Right=scan_data[270]
    print(f'Right: {Right}')
    Back=scan_data[0]
    print(f'Back: {Back}')
    return Front, Left, Right, Back
 
# Jeżeli w dwóch iteracjach na danym indeksie jest ta sama watość to znaczy że jest to błąd i należy się tej wartości pozbyć zerując ją. Wiązka nie wraca do lidaru ze względu na błędne odbicie.
# Można zooptymalizować?
def lidar_fix(scan_data, scan_data_before):
    for i in range(len(scan_data)):
        if scan_data[i] == scan_data_before[i]:
            scan_data[i] = 0
    return scan_data


if __name__ == '__main__':
    client_id = f'lidar'
    topic = "mqtt/lidar"
    client = connect_mqtt(client_id, BROKER, PORT)
    scan_data = [0] * 360
    scan_data_before = [0] * 360
    try:
        for scan in LIDAR.iter_scans():
            for (_, angle, distance) in scan:
                    scan_data[min([359, floor(angle)])] = distance/10
            scan_data = lidar_fix(scan_data, scan_data_before)
            scan_data_before = copy.deepcopy(scan_data)
            scan_data = [int(i) for i in scan_data]
            mqtt_mess=f"{scan_data}"
            mqtt_pub.publish(client, topic, mqtt_mess)
    except KeyboardInterrupt:
        print('Stopping.')
        LIDAR.stop()
        LIDAR.disconnect()