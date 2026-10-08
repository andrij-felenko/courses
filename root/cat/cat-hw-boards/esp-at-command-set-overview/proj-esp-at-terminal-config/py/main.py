"""Головний виконуваний скрипт для діагностики та налаштування ESP-модуля через ESP-AT."""

import sys
import time
import serial

from esp_at_client import ESPATClient, ESPATError


def main() -> None:
    # Конфігураційні параметри послідовного з'єднання
    port_name = "COM3"  # Для Linux/macOS скоригуйте на '/dev/ttyUSB0' або '/dev/ttyS0'
    initial_baudrate = 115200
    target_baudrate = 9600

    print("=" * 70)
    print(" ДІАГНОСТИКА ТА КЕРУВАННЯ ESP-МОДУЛЕМ ЧЕРЕЗ ESP-AT (PySerial)")
    print("=" * 70)
    print(f"[ІНІЦІАЛІЗАЦІЯ] Спроба відкриття порту {port_name} на швидкості {initial_baudrate} бод...")

    try:
        # Створення клієнта та автоматичне відкриття порту через контекстний менеджер
        with ESPATClient(port=port_name, baudrate=initial_baudrate, timeout=2.0) as client:
            print("[ІНФО] Послідовний порт успішно відкрито.\n")

            # КРОК 1: Перевірка зв'язку (команда AT)
            print("[КРОК 1] Виконання первинної діагностики зв'язку (команда AT)...")
            if client.test_at():
                print(" -> [УСПІХ] ESP-модуль відповідає та готовий до роботи (отримано OK).\n")

            # КРОК 2: Зчитування системної інформації та версії прошивки (команда AT+GMR)
            print("[КРОК 2] Зчитування системних відомостей модуля (команда AT+GMR)...")
            sys_info = client.get_system_info()
            print(" -> Отримані відомості про прошивку:")
            for line in sys_info:
                print(f"    | {line}")
            print(" -> [УСПІХ] Системну інформацію успішно прочитано.\n")

            # КРОК 3: Програмна зміна швидкості UART (команда AT+UART_CUR)
            print(f"[КРОК 3] Програмне переналаштування швидкості UART на {target_baudrate} бод...")
            client.change_uart_config(baudrate=target_baudrate)
            print(f" -> Команду AT+UART_CUR надіслано. Швидкість PySerial переключено на {target_baudrate} бод.")

            # Перевірка відновлення зв'язку на новій швидкості
            print(f" -> Перевірка зв'язку на новій швидкості ({target_baudrate} бод)...")
            if client.test_at():
                print(f" -> [УСПІХ] Зв'язок на швидкості {target_baudrate} бод успішно підтверджено (OK).\n")

            # КРОК 4: Повернення до початкової швидкості UART (115200 бод)
            print(f"[КРОК 4] Повернення швидкості UART до початкового значення ({initial_baudrate} бод)...")
            client.change_uart_config(baudrate=initial_baudrate)
            print(f" -> Швидкість PySerial відновлено до {initial_baudrate} бод.")

            # Перевірка відновлення зв'язку на початковій швидкості
            print(f" -> Перевірка відновлення зв'язку ({initial_baudrate} бод)...")
            if client.test_at():
                print(f" -> [УСПІХ] Початкову швидкість обміну {initial_baudrate} бод успішно відновлено (OK).\n")

            print("=" * 70)
            print(" ДІАГНОСТИКА ТА ПЕРЕНАЛАШТУВАННЯ УСПІШНО ЗАВЕРШЕНІ")
            print("=" * 70)

    except ESPATError as err:
        print(f"\n[ПОМИЛКА ESP-AT] Збій під час виконання AT-протоколу: {err}")
    except serial.SerialException as err:
        print(f"\n[ПОМИЛКА UART] Не вдалося відкрити або налаштувати порт {port_name}: {err}")
        print("[ІНФО] Переконайтеся, що ESP-модуль фізично підключений та вказано правильний COM-порт.")
    except Exception as err:
        print(f"\n[КРИТИЧНА ПОМИЛКА] Несподіваний збій виконання: {err}")


if __name__ == "__main__":
    main()
