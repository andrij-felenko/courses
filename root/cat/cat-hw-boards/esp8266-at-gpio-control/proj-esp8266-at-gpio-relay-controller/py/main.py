"""Головний виконуваний скрипт для керування GPIO виводами ESP8266 через AT-команди.

Демонструє ініціалізацію з'єднання через pyserial.Serial, покрокове налаштування режимів,
безпечне керування силовим реле з урахуванням конфігураційних виводів завантаження
(strapping pins GPIO0, GPIO2, GPIO15) та програмний контроль фактичного стану.
"""

import sys
import time
import serial
from esp8266_gpio import ESP8266GPIOController, ESP8266GPIOError


def main() -> None:
    # Параметри підключення до послідовного порту UART
    port_name = "COM3"
    baud_rate = 115200

    print(f"[ІНІЦІАЛІЗАЦІЯ] Спроба відкриття послідовного порту {port_name} ({baud_rate} бод)...")

    try:
        # Ініціалізація з'єднання через бібліотеку PySerial (serial.Serial)
        ser = serial.Serial(port=port_name, baudrate=baud_rate, timeout=2.0)
    except serial.SerialException as err:
        print(f"[ПОМИЛКА] Не вдалося відкрити послідовний порт {port_name}: {err}")
        print("[ІНФО] Для фізичної роботи перевірте підключення ESP8266 та ім'я COM-порту.")
        sys.exit(1)

    try:
        # Створення контролера GPIO з передачею об'єкта serial.Serial
        controller = ESP8266GPIOController(port=ser)

        print("[КРОК 1] Перевірка готовності модуля ESP8266 (команда AT)...")
        if controller.test_connection():
            print("[УСПІХ] Модуль ESP8266 успішно відповідає на AT-команди.")

        # УВАГА щодо конфігураційних виводів завантаження (Strapping Pins):
        # - GPIO0:  Визначає режим завантаження. При скиданні/ввімкненні має бути HIGH (Flash Boot).
        #           Якщо при подачі живлення GPIO0 підтягнутий до LOW, ESP8266 переходить у режим UART Flashing.
        # - GPIO2:  Має бути підтягнутий до HIGH під час завантаження.
        # - GPIO15: Має бути підтягнутий до LOW під час завантаження.
        # Підключення силових реле до strapping pins може спровокувати небажані клацання при старті
        # або блокування завантаження ESP8266. Тому вибираємо безпечні виводи загального призначення:
        relay_pin = 4  # Безпечний вивід GPIO4 для силового реле
        sensor_pin = 5  # Безпечний вивід GPIO5 для зчитування стану датчика

        print("\n[КРОК 2] Покрокова конфігурація режимів виводів ESP8266...")
        print(f" -> Налаштування GPIO{relay_pin} як OUTPUT (режим виходу)...")
        controller.set_pin_mode(relay_pin, ESP8266GPIOController.PIN_MODE_OUTPUT)

        print(f" -> Налаштування GPIO{sensor_pin} як INPUT_PULLUP (режим входу з внутрішньою підтяжкою)...")
        controller.set_pin_mode(sensor_pin, ESP8266GPIOController.PIN_MODE_INPUT_PULLUP)

        print("\n[КРОК 3] Безпечне керування силовим реле та верифікація станів...")

        # 1. Перемикання реле у ввімкнений стан (HIGH)
        print(f" -> Перемикання реле: встановлення GPIO{relay_pin} = HIGH")
        controller.write_pin(relay_pin, ESP8266GPIOController.HIGH)

        # Затримка для стабілізації переходів на виводі та механічного спрацьовування реле
        stabilization_delay = 0.5
        time.sleep(stabilization_delay)

        # Програмний контроль фактичного стану виводу шляхом зворотного зчитування (AT+PINREAD)
        actual_state_high = controller.read_pin(relay_pin)
        print(f" -> Програмна верифікація: зчитаний стан GPIO{relay_pin} = {actual_state_high}")

        if actual_state_high == ESP8266GPIOController.HIGH:
            print("[ПІДТВЕРДЖЕНО] Реле успішно переведено у ввімкнений стан (HIGH).")
        else:
            print(f"[УВАГА] Невідповідність стану! Очікувалося HIGH, зчитано {actual_state_high}")

        # Утримання увімкненого стану
        time.sleep(1.0)

        # 2. Перемикання реле у вимкнений стан (LOW)
        print(f"\n -> Перемикання реле: встановлення GPIO{relay_pin} = LOW")
        controller.write_pin(relay_pin, ESP8266GPIOController.LOW)
        time.sleep(stabilization_delay)

        actual_state_low = controller.read_pin(relay_pin)
        print(f" -> Програмна верифікація: зчитаний стан GPIO{relay_pin} = {actual_state_low}")

        if actual_state_low == ESP8266GPIOController.LOW:
            print("[ПІДТВЕРДЖЕНО] Реле успішно переведено у вимкнений стан (LOW).")
        else:
            print(f"[УВАГА] Невідповідність стану! Очікувалося LOW, зчитано {actual_state_low}")

        print("\n[КРОК 4] Зчитування стану вхідного виводу датчика...")
        sensor_value = controller.read_pin(sensor_pin)
        print(f" -> Фактичний стан виводу GPIO{sensor_pin} (датчик): {sensor_value}")

    except ESP8266GPIOError as err:
        print(f"[ПОМИЛКА ESP8266] Збій виконання AT-команди: {err}")
    except Exception as err:
        print(f"[КРИТИЧНА ПОМИЛКА] Непередбачений збій: {err}")
    finally:
        if "ser" in locals() and ser.is_open:
            ser.close()
            print("\n[ЗАКЕРШЕННЯ] Послідовний порт успішно закрито.")


if __name__ == "__main__":
    main()
