#!/usr/bin/env python3
"""
Діагностика та петльове тестування (loopback) USB-UART перетворювача CH340.
Скрипт демонструє конфігурацію послідовного порту, маніпулювання лініями DTR/RTS
для керування скиданням/прошивкою мікроконтролерів та верифікацію цілісності даних.
"""

import sys
import time
import serial
from serial.tools import list_ports


def find_ch340_port() -> str | None:
    """
    Пошук послідовного порту пристрою CH340 в системі за Vendor ID (VID) та Product ID (PID).
    CH340 зазвичай має VID=0x1A86 та PID=0x7523.
    """
    ch340_vid = 0x1A86
    ch340_pid = 0x7523

    ports = list_ports.comports()
    for port in ports:
        if port.vid == ch340_vid and port.pid == ch340_pid:
            print(f"[+] Знайдено CH340 на порту: {port.device} ({port.description})")
            return port.device
    return None


def control_dtr_rts_signals(ser: serial.Serial) -> None:
    """
    Демонстрація керування службовими сигнальними лініями DTR та RTS.

    Увага: у більшості планок CH340 сигнальні лінії DTR# та RTS# є інверсними (Active Low).
    В pySerial:
      - dtr = True / rts = True  -> встановлює логічний 0 (0 В, низький рівень)
      - dtr = False / rts = False -> встановлює логічну 1 (3.3В / 5В, високий рівень)
    """
    print("\n--- 1. Керування лініями DTR та RTS ---")

    # 1. Початковий стан: інактивація сигналів (високий рівень)
    ser.dtr = False
    ser.rts = False
    time.sleep(0.1)
    print("  Початковий стан: DTR=Inactive (HIGH), RTS=Inactive (HIGH)")

    # 2. Імітація сигналу скидання (Reset pulse для Arduino / ESP)
    # Імпульс DTR у низький рівень (True в pySerial)
    print("  Генерація імпульсу RESET (DTR -> LOW на 100 мс)...")
    ser.dtr = True
    time.sleep(0.1)
    ser.dtr = False
    time.sleep(0.1)
    print("  Скидання завершено (DTR -> HIGH).")

    # 3. Імітація комбінації для входу в бутлоадер ESP8266/ESP32 (GPIO0 = LOW, RESET pulse)
    print("  Генерація сигналів для входу в режим прошивки (Bootloader mode)...")
    # GPIO0 підтягується до RTS (активний 0), RESET підтягується до DTR
    ser.rts = True   # GPIO0 = 0V
    ser.dtr = True   # RESET = 0V
    time.sleep(0.05)
    ser.dtr = False  # Відпускаємо RESET (мікроконтролер стартує з GPIO0=0)
    time.sleep(0.1)
    ser.rts = False  # Відпускаємо GPIO0 у нормальний стан
    print("  Сигнали переведення в режим прошивки успішно згенеровано.")


def perform_loopback_test(ser: serial.Serial, test_data: bytes) -> bool:
    """
    Проведення петльового тестування (Loopback Test).
    Вимагає замкнених між собою контактів TXD та RXD на платі CH340.
    """
    print("\n--- 2. Петльове тестування (Loopback Test TXD -> RXD) ---")

    # Очищення вхідного та вихідного буферів перед тестом
    ser.reset_input_buffer()
    ser.reset_output_buffer()

    print(f"  Надсилання {len(test_data)} байт(ів) даних...")

    start_time = time.time()
    # Запис даних у порт
    bytes_written = ser.write(test_data)
    ser.flush()  # Чекаємо на повне завершення відправки байтів

    print(f"  Записано в порт: {bytes_written} байт. Зчитування відповіді з таймаутом {ser.timeout}s...")

    # Зчитування очікуваної кількості байтів з урахуванням таймауту
    received_data = ser.read(len(test_data))
    elapsed_time = time.time() - start_time

    print(f"  Прочитано з порту: {len(received_data)} байт (витрачено {elapsed_time:.3f} сек).")

    # Перевірка результатів тестування
    if len(received_data) < len(test_data):
        print(f"  [ПОМИЛКА] Таймаут зчитування! Передано {len(test_data)} B, отримано {len(received_data)} B.")
        print("  Перевірте, чи фізично замкнені контакти TXD та RXD на мосту CH340.")
        return False

    if received_data == test_data:
        print("  [УСПІХ] Передані та отримані дані повністю збігаються!")
        return True
    else:
        print("  [ПОМИЛКА] Дані пошкоджено під час передачі!")
        print(f"    Очікувалось: {test_data!r}")
        print(f"    Отримано:    {received_data!r}")
        return False


def main() -> None:
    # 1. Пошук або визначення порту CH340
    port_name = find_ch340_port()
    if not port_name:
        # Аргумент командного рядка або дефолтний порт
        if len(sys.argv) > 1:
            port_name = sys.argv[1]
        else:
            # Залежно від ОС за замовчуванням
            port_name = "COM3" if sys.platform.startswith("win") else "/dev/ttyUSB0"
            print(f"[!] Пристрій CH340 не виявлено автоматично. Використовується порт за замовчуванням: {port_name}")

    # 2. Налаштування параметрів підключення
    baudrate = 115200
    read_timeout = 2.0
    write_timeout = 2.0

    print(f"Відкриття послідовного порту {port_name} на швидкості {baudrate} baud...")

    try:
        # Відкриття та конфігурація порту CH340 за допомогою pySerial
        with serial.Serial(
            port=port_name,
            baudrate=baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=read_timeout,
            write_timeout=write_timeout,
        ) as ser:
            print(f"Порт {ser.name} успішно відкрито.")

            # Виконання маніпуляцій з DTR / RTS
            control_dtr_rts_signals(ser)

            # Набір тестових даних для перевірки (ASCII + бінарні байти)
            test_payload = b"CH340_LOOPBACK_TEST_ASCII_0123456789\x00\xFF\x55\xAA"

            # Проведення петльового тестування
            success = perform_loopback_test(ser, test_payload)

            if success:
                print("\n[РЕЗУЛЬТАТ] CH340 повністю справний та готовий до роботи.")
            else:
                print("\n[РЕЗУЛЬТАТ] Тест не пройдено. Перевірте лінії зв'язку.")

    except serial.SerialException as e:
        print(f"\n[ПОМИЛКА КЛІЄНТА] Не вдалося відкрити або працювати з портом {port_name}: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[НЕОЧІКУВАНА ПОМИЛКА] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
