import os
import periphery
import subprocess
import keyboard
import signal
    
if __name__ == "__main__":
        try:
                pwm_R = periphery.PWM(0, 0)
                pwm_L = periphery.PWM(1, 0)
                pwm_R.frequency=1e3
                pwm_L.frequency=1e3
                pwm_R.enable
                pwm_L.enable
        except OSError:
                print("PWM został juz zainicjowany.")
        