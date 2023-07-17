from periphery import GPIO
import time

Step_Pin=73
Dir_Pin=74
Step_GPIO=GPIO(Step_Pin,"out")
Dir_GPIO=GPIO(Dir_Pin,"out")
Direction=True
def Stepper_motor(Direction):
    Dir_GPIO.write(Direction)
    for y in range (10):
        for x in range (200):
            try:
                Step_GPIO.write(True)
                time.sleep(0.005)
                Step_GPIO.write(False)
                time.sleep(0.005)
            except KeyboardInterrupt:
                Step_GPIO.write(False)
                break
            except IOError:
                print("IOErr")
                break

if __name__ == "__main__":
     Stepper_motor(1) #1 for CW - clockwise 0 for counterclockwise