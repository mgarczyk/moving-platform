from periphery import GPIO
import time

LED_Pin=73
LED_GPIO=GPIO(LED_Pin,"out")
while True:
    try:
        LED_GPIO.write(True)
        time.sleep(0.001)
        LED_GPIO.write(False)
        time.sleep(0.001)
    except KeyboardInterrupt:
        LED_GPIO.write(False)
        break
    except IOError:
        print("IOErr")
        break