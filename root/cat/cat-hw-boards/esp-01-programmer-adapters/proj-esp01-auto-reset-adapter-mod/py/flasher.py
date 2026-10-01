"""
Скрипт автоматизації автоскидання та прошивання модулів ESP-01 / ESP8266
за допомогою керування лініями DTR/RTS USB-UART адаптера та бібліотеки esptool.
"""

import sys
import time
import argparse
from typing import Dict, Any, Optional

import serial
import esptool


class ESP01AutoFlasher:
    """
    Клас-обгортка для керування апаратним автоскидом ESP-01 у режим
    завантажувача (bootloader) та виконання діагностики і прошивки.
    """

    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 3.0):
        """
        Ініціалізує параметри з'єднання з послідовним портом.

        :param port: Назва послідовного порту (наприклад, 'COM3' або '/dev/ttyUSB0')
        :param baudrate: Швидкість обміну даними в бодах
        :param timeout: Таймаут для операцій зчитування порту в секундах
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.esp: Optional[esptool.ESPLoader] = None

    def hard_reset_to_bootloader(self) -> None:
        """
        Формує часову послідовність сигналів DTR та RTS для NPN-автоскиду.

        Алгоритм переведення ESP8266 у режим завантажувача (GPIO0 = 0V при розблокуванні RST):
        1. DTR = 0 (low), RTS = 1 (high)  -> Q1 ON (GPIO0 підтягується до 0V)
        2. DTR = 1 (high), RTS = 0 (low)  -> Q2 ON (RST притискається до 0V)
        3. DTR = 0 (low), RTS = 0 (low)   -> Q1, Q2 OFF (RST зростає до 3.3V, GPIO0 зчитується як 0V)
        """
        print(f"[i] Ініціалізація апаратного автоскиду на порту {self.port}...")
        try:
            with serial.Serial(self.port, self.baudrate, timeout=self.timeout) as ser:
                # Крок 1: Встановлюємо GPIO0 = 0V (DTR=False / RTS=True)
                ser.setDTR(False)
                ser.setRTS(True)
                time.sleep(0.1)

                # Крок 2: Подаємо імпульс скидання RST = 0V (DTR=True / RTS=False)
                ser.setDTR(True)
                ser.setRTS(False)
                time.sleep(0.1)

                # Крок 3: Знімаємо скидання RST = 3.3V при активному GPIO0 = 0V
                ser.setDTR(False)
                ser.setRTS(False)
                time.sleep(0.05)

            print("[+] Автоскид виконано. Модуль перебуває в режимі Bootloader.")
        except serial.SerialException as err:
            raise RuntimeError(f"Помилка роботи з послідовним портом {self.port}: {err}") from err

    def hard_reset_to_app(self) -> None:
        """
        Виконує звичайний перезапуск мікроконтролера в режим виконання програми (GPIO0 = 3.3V).
        """
        print("[i] Перезапуск мікроконтролера в режим виконання користувацького коду...")
        try:
            with serial.Serial(self.port, self.baudrate, timeout=self.timeout) as ser:
                ser.setDTR(True)
                ser.setRTS(False)
                time.sleep(0.1)
                ser.setDTR(False)
                ser.setRTS(False)
            print("[+] Мікроконтролер успішно перезапущено.")
        except serial.SerialException as err:
            print(f"[!] Помилка при виконанні перезапуску: {err}")

    def connect(self) -> None:
        """
        Підключається до завантажувача ESP8266 за допомогою бібліотеки esptool.
        """
        self.hard_reset_to_bootloader()
        print("[i] З'єднання з ROM-завантажувачем ESP8266...")
        try:
            self.esp = esptool.ESPLoader.detect_chip(
                port=self.port,
                baud=self.baudrate,
                connect_attempts=5
            )
            print(f"[+] Успішно підключено до чипа: {self.esp.CHIP_NAME}")
        except esptool.FatalError as err:
            raise RuntimeError(f"Не вдалося з'єднатися з завантажувачем ESP8266: {err}") from err

    def read_flash_id(self) -> Dict[str, Any]:
        """
        Зчитує ідентифікатор та характеристики Flash-пам'яті модуля ESP-01.

        :return: Словник із полями 'manufacturer_id', 'device_id', 'flash_size'
        """
        if not self.esp:
            self.connect()

        print("[i] Зчитання характеристик Flash-пам'яті...")
        try:
            flash_id = self.esp.read_flash_id()
            mfg_id = (flash_id >> 16) & 0xFF
            dev_id = flash_id & 0xFFFF
            size_name = esptool.FLASH_SIZES.get(self.esp.flash_size, "Невідомо")

            info = {
                "flash_id": hex(flash_id),
                "manufacturer_id": hex(mfg_id),
                "device_id": hex(dev_id),
                "size_bytes": self.esp.flash_size,
                "size_human": size_name
            }
            print(f"[+] Виробник Flash ID: {info['manufacturer_id']}")
            print(f"[+] Модель Flash ID: {info['device_id']}")
            print(f"[+] Визначений розмір Flash: {info['size_human']}")
            return info
        except esptool.FatalError as err:
            raise RuntimeError(f"Помилка зчитування Flash ID: {err}") from err

    def write_flash(self, image_path: str, offset: int = 0x0) -> bool:
        """
        Записує бінарний образ прошивки у Flash-пам'ять ESP-01.

        :param image_path: Шлях до бінарного файлу (.bin)
        :param offset: Зміщення у Flash-пам'яті для запису (за замовчуванням 0x0)
        :return: True в разі успішного запису
        """
        if not self.esp:
            self.connect()

        print(f"[i] Запис прошивки '{image_path}' за адресою {hex(offset)}...")
        try:
            with open(image_path, "rb") as image_file:
                image_data = image_file.read()

            print(f"[i] Розмір прошивки: {len(image_data)} байт.")

            # Використання внутрішнього механізму esptool для запису блоків пам'яті
            self.esp.flash_begin(size=len(image_data), offset=offset)
            block_size = esptool.ESPLoader.FLASH_WRITE_SIZE
            blocks = (len(image_data) + block_size - 1) // block_size

            for seq in range(blocks):
                block = image_data[seq * block_size : (seq + 1) * block_size]
                # Паддинг останнього блоку до block_size в разі потреби
                if len(block) < block_size:
                    block += b"\xFF" * (block_size - len(block))

                self.esp.flash_block(block, seq)
                progress = int(((seq + 1) / blocks) * 100)
                sys.stdout.write(f"\r[>] Прогрес запису: {progress}%")
                sys.stdout.flush()

            print("\n[+] Запис прошивки успішно завершено!")
            self.esp.flash_finish(reboot=False)
            self.hard_reset_to_app()
            return True

        except FileNotFoundError:
            raise FileNotFoundError(f"Файл прошивки '{image_path}' не знайдено.")
        except esptool.FatalError as err:
            raise RuntimeError(f"Помилка запису у Flash-пам'ять: {err}") from err


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Автоматизація прошивки та діагностики модулів ESP-01 (ESP8266)"
    )
    parser.add_argument("-p", "--port", required=True, help="Послідовний порт (наприклад, COM3 або /dev/ttyUSB0)")
    parser.add_argument("-b", "--baud", type=int, default=115200, help="Швидкість обміну (за замовчуванням: 115200)")
    parser.add_argument("--read-id", action="store_true", help="Зчитати характеристики Flash-пам'яті")
    parser.add_argument("--flash", type=str, help="Шлях до бінарного файлу прошивки (.bin)")
    parser.add_argument("--offset", type=lambda x: int(x, 0), default=0x0, help="Зміщення запису (за замовчуванням: 0x0)")

    args = parser.parse_args()

    flasher = ESP01AutoFlasher(port=args.port, baudrate=args.baud)

    try:
        if args.read_id:
            flasher.read_flash_id()
        elif args.flash:
            flasher.write_flash(image_path=args.flash, offset=args.offset)
        else:
            print("[i] Операцію не вказано. Виконується діагностичне зчитування Flash ID.")
            flasher.read_flash_id()
    except Exception as err:
        print(f"[!] Критична помилка виконання: {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
