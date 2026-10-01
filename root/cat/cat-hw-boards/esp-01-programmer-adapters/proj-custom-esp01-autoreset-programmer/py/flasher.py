import sys
import time
import subprocess
import argparse
from pathlib import Path

try:
    import serial
    import serial.tools.list_ports
except ImportError:
    serial = None


class ESP01Programmer:
    """
    Клас-обгортка для керування послідовним портом, виклику утиліти esptool
    та генерації апаратного скидання у режим завантажувача через лінії DTR/RTS.
    """

    def __init__(self, port: str = None, baudrate: int = 115200):
        self.baudrate = baudrate
        self.port = port or self.auto_detect_port()

    def auto_detect_port(self) -> str:
        """
        Автоматично знаходить перший доступний USB-UART адаптер (CH340, CP2102, FT232).
        """
        if serial is None:
            raise RuntimeError(
                "Бібліотека PySerial не встановлена. Встановіть її за допомогою: pip install pyserial"
            )

        ports = list(serial.tools.list_ports.comports())
        for p in ports:
            description = p.description.lower()
            if any(chip in description for chip in ["ch340", "cp210", "ft232", "usb-to-uart", "usb serial"]):
                print(f"[+] Виявлено програматор на порту: {p.device} ({p.description})")
                return p.device

        if ports:
            first_port = ports[0].device
            print(f"[!] Конвертер не розпізнано за назвою. Використовуємо перший доступний порт: {first_port}")
            return first_port

        raise RuntimeError("Не знайдено жодного підключеного COM-порту для програмування ESP-01.")

    def trigger_bootloader_reset(self) -> bool:
        """
        Переводить ESP-01 у режим завантажувача (Bootloader Mode) за допомогою
        транзисторної схеми автоскидання на лініях DTR та RTS.
        
        Схема роботи транзисторів S8050/S8550:
        - DTR=Low (False), RTS=High (True)  => GPIO0 притягується до GND (0)
        - DTR=High (True), RTS=High (True)  => EN/RST притягується до GND (Reset pulse)
        - DTR=Low (False), RTS=Low (False)  => Всі транзистори закриті, виводи у затяжці 3.3V
        """
        if serial is None:
            print("[!] PySerial відсутній. Пропускаємо апаратне скидання DTR/RTS.")
            return False

        print(f"[*] Формування імпульсів скидання DTR/RTS на порту {self.port}...")
        try:
            with serial.Serial(self.port, self.baudrate) as ser:
                ser.setDTR(False)
                ser.setRTS(False)
                time.sleep(0.05)

                # Крок 1: Фіксація GPIO0 у низькому рівні (DTR=0, RTS=1 -> GPIO0=0)
                ser.setDTR(False)
                ser.setRTS(True)
                time.sleep(0.05)

                # Крок 2: Короткий імпульс скидання на лінію RST (DTR=1, RTS=1 -> RST=0)
                ser.setDTR(True)
                ser.setRTS(True)
                time.sleep(0.1)

                # Крок 3: Зняття скидання при збереженні нульового стану GPIO0 (DTR=0, RTS=1 -> RST=1, GPIO0=0)
                ser.setDTR(False)
                ser.setRTS(True)
                time.sleep(0.05)

                # Крок 4: Завершення послідовності скидання (DTR=0, RTS=0)
                ser.setDTR(False)
                ser.setRTS(False)
                time.sleep(0.1)

            print("[+] ESP-01 успішно переведено у режим завантажувача (Bootloader).")
            return True
        except serial.SerialException as e:
            print(f"[-] Помилка доступу до послідовного порту {self.port}: {e}")
            return False

    def _execute_esptool(self, commands: list) -> tuple[int, str, str]:
        """
        Викликає утиліти esptool через системний subprocess.
        """
        cmd = [sys.executable, "-m", "esptool", "--port", self.port, "--baud", str(self.baudrate)] + commands
        print(f"[*] Виконання команди: {' '.join(cmd)}")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            return result.returncode, result.stdout, result.stderr
        except FileNotFoundError:
            err = "Утиліту esptool не знайдено. Встановіть її через 'pip install esptool'."
            print(f"[-] {err}")
            return 1, "", err

    def read_chip_info(self) -> bool:
        """
        Зчитує ідентифікаційні дані чипа ESP8266 (MAC-адресу та тип флеш-пам'яті).
        """
        self.trigger_bootloader_reset()
        code, stdout, stderr = self._execute_esptool(["flash_id"])
        
        if code == 0:
            print("[+] Інформацію про чип успішно отримано:")
            for line in stdout.splitlines():
                if any(key in line for key in ["Detecting chip type", "MAC:", "Manufacturer:", "Device:", "Detected flash size:"]):
                    print(f"    {line.strip()}")
            return True
        else:
            print(f"[-] Не вдалося зчитати дані чипа:\n{stderr or stdout}")
            return False

    def flash_firmware(self, firmware_path: str, address: str = "0x00000", verify: bool = True) -> bool:
        """
        Стирає та записує бінарний образ прошивки у флеш-пам'ять ESP-01.
        """
        fw_file = Path(firmware_path)
        if not fw_file.exists():
            print(f"[-] Файл прошивки '{firmware_path}' не знайдено.")
            return False

        print(f"[*] Підготовка до запису прошивки: {fw_file.name} ({fw_file.stat().st_size} байт)")
        self.trigger_bootloader_reset()

        cmd_args = ["write_flash"]
        if verify:
            cmd_args.append("--verify")
        cmd_args.extend([address, str(fw_file)])

        code, stdout, stderr = self._execute_esptool(cmd_args)
        if code == 0:
            print(f"[+] Прошивку {fw_file.name} успішно записано за адресою {address}!")
            return True
        else:
            print(f"[-] Помилка під час запису прошивки:\n{stderr or stdout}")
            return False


def main():
    parser = argparse.ArgumentParser(
        description="Скрипт автоматичного програмування ESP-01 через адаптери з DTR/RTS."
    )
    parser.add_argument("-p", "--port", type=str, help="Послідовний COM-порт (наприклад, COM3 або /dev/ttyUSB0)")
    parser.add_argument("-b", "--baud", type=int, default=115200, help="Швидкість обміну (за замовчуванням 115200)")
    parser.add_argument("--info", action="store_true", help="Зчитати інформацію про чип та флеш-пам'ять")
    parser.add_argument("--flash", type=str, help="Шлях до бінарного файла прошивки (.bin)")
    parser.add_argument("--addr", type=str, default="0x00000", help="Адреса запису у флеш (за замовчуванням 0x00000)")

    args = parser.parse_args()

    try:
        programmer = ESP01Programmer(port=args.port, baudrate=args.baud)

        if args.info:
            programmer.read_chip_info()
        elif args.flash:
            programmer.flash_firmware(firmware_path=args.flash, address=args.addr)
        else:
            print("[!] Не вказано дію. Використовуйте --info для перевірки або --flash <file.bin> для прошивання.")
            parser.print_help()

    except Exception as e:
        print(f"[-] Критична помилка виконання: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
