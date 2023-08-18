import time
from periphery import GPIO

# Ustawienie numerów pinów GPIO, do których są podłączone enkodery
ENCODER1_PIN_A = 74
ENCODER1_PIN_B = 158
ENCODER2_PIN_A = 76
ENCODER2_PIN_B = 73

# Inicjalizacja obiektów GPIO
encoder1_gpio_a = GPIO(ENCODER1_PIN_A, "in")
encoder1_gpio_b = GPIO(ENCODER1_PIN_B, "in")
encoder2_gpio_a = GPIO(ENCODER2_PIN_A, "in")
encoder2_gpio_b = GPIO(ENCODER2_PIN_B, "in")

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
            return encoder_speed /(48*99)

# Główna pętla programu
try:
    while True:
        encoder1_speed = read_encoder_speed(encoder1_gpio_a, encoder1_gpio_b)
        encoder2_speed = read_encoder_speed(encoder2_gpio_a, encoder2_gpio_b)
        print("Encoder 1: Prędkość =", encoder1_speed, "zmian/sek")
        print("Encoder 2: Prędkość =", encoder2_speed, "zmian/sek")

except KeyboardInterrupt:
    pass

# Zakończenie programu
encoder1_gpio_a.close()
encoder1_gpio_b.close()
encoder2_gpio_a.close()
encoder2_gpio_b.close()
