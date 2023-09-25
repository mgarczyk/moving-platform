import json
from periphery import GPIO

try:
    with open ("config.json") as config_f:
        config = json.load(config_f)
        DIR_LIFT = GPIO(config["DIR_LIFT"], "out")
        SET_PWM_LIFT = GPIO(config["SET_PWM_LIFT"], "out")
        config_f.close()
except FileNotFoundError:
    print("Brak pliku konfiguracyjnego.")
    exit()

def stop():
    print("Reseting lift.")
    SET_PWM_LIFT.write(False)
    

if __name__ == '__main__':
    stop()