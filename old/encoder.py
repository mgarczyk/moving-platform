import time
import math
import mqtt_pub
import mqtt_sub
from periphery import GPIO

# Ustawienie numerów pinów GPIO, do których są podłączone enkodery
ENCODER1_PIN_A = 74
ENCODER1_PIN_B = 158
ENCODER2_PIN_A = 76
ENCODER2_PIN_B = 73

# Inicjalizacja obiektów GPIO
encoder_right_a = GPIO(ENCODER1_PIN_A, "in")
encoder_right_b = GPIO(ENCODER1_PIN_B, "in")
encoder_left_a = GPIO(ENCODER2_PIN_A, "in")
encoder_left_b = GPIO(ENCODER2_PIN_B, "in")

# Funkcja do odczytu prędkości enkodera
def read_encoder_speed(gpio_a, gpio_b):
    prev_value_a = gpio_a.read()
    prev_value_b = gpio_b.read()
    change_count = 0
    start_time = time.time()
    while True:
        current_value_a = gpio_a.read()
        current_value_b = gpio_b.read()
        if current_value_a != prev_value_a or current_value_b != prev_value_b:
            change_count += 1
            prev_value_a = current_value_a
            prev_value_b = current_value_b
        elapsed_time = time.time() - start_time
        if elapsed_time >= 1.0:  # Odczytuj prędkość co 1 sekundę
            encoder_speed = change_count / elapsed_time
            robot_velocity = round((encoder_speed /(48*99)) *  math.pi * 0.102, 2) #dzielimy odczyt przez częstotliwość impulsu mnożoną razy przekładnię. 2*pi*r jako obwód koła, co daje nam przejechaną drogę oraz prędkość.
            return robot_velocity

# Główna pętla programu
try:
    while True:
        encoder_right_speed = read_encoder_speed(encoder_right_a, encoder_right_b)
        encoder_left_speed = read_encoder_speed(encoder_left_a, encoder_left_b)
except KeyboardInterrupt:
    pass

# Zakończenie programu
encoder_right_a.close()
encoder_left_a.close()
encoder_right_b.close()
encoder_left_a.close()
