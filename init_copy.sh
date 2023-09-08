#!/bin/bash
cd /home/rock/moving_platform
echo "Nadanie uprawnień do USB"
chmod 666 /dev/ttyUSB0
echo "Zatrzymanie usługi debbugera no portach UART2"
systemctl stop serial-getty@ttyS2.service
echo "Inicjacja PWM"
echo 0 > /sys/class/pwm/pwmchip0/export
echo 0 > /sys/class/pwm/pwmchip1/export
echo "Ustawienie parametrów PWM"
python3 init_PWM.py
