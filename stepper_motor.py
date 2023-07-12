from periphery import GPIO
import time

STEPPER_PIN=73
STEPPER_GPIO=GPIO(STEPPER_PIN,"out")
while True:
    try:
        STEPPER_GPIO.write(True)
        time.sleep(0.001)
        STEPPER_GPIO.write(False)
        time.sleep(0.001)
    except KeyboardInterrupt:
        STEPPER_GPIO.write(False)
        break
    except IOError:
        print("IOErr")
        break