import time
import pigpio

SERVO_PIN = 18  # Вивід GPIO з підтримкою апаратного таймера

# Підключення до демона pigpio
pi = pigpio.pi()

if not pi.connected:
    print("Не вдалося підключитися до демона pigpio")
    exit(1)

try:
    # Переведення вала в нейтральне положення (1500 мкс = 90 градусів)
    pi.set_servo_pulsewidth(SERVO_PIN, 1500)
    time.sleep(0.5)

    # Встановлення тривалості 1250 мкс (45 градусів)
    pi.set_servo_pulsewidth(SERVO_PIN, 1250)
    time.sleep(0.5)

finally:
    # Зупинка генерації імпульсів (0 = вимкнути сервоканал)
    pi.set_servo_pulsewidth(SERVO_PIN, 0)
    pi.stop()
