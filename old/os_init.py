# Sterowanie silnikami - kierunki oraz PWM przeniesione na Arduino, ze względu na opóźnienienia Linuxa.
import os
import periphery

def pwm_sys_init():
    try:
        os.system("date")
        os.system("echo 0 > /sys/class/pwm/pwmchip0/export")
    except OSError:
        print("PWM system error")

def pwm_init():
    try:
        pwm_R = periphery.PWM(0, 0)
        pwm_L = periphery.PWM(1, 0)
        pwm_R.frequency=1e3
        pwm_L.frequency=1e3
        pwm_R.enable
        pwm_L.enable
        pwm_R.duty_cycle = 1.0
        pwm_L.duty_cycle = 1.0
        print("PWM frequency set")
    except OSError:
        print("PWM został juz zainicjowany.")

pwm_sys_init()
pwm_init()

        