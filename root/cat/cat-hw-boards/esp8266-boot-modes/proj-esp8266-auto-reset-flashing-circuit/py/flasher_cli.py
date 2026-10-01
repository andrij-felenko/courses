import sys
import argparse
import time
import subprocess
from esp_reset_controller import ESPResetController

class ESPFlasher:
    """
    Клас-обгортка для автоматизації прошивання ESP8266 через esptool API чи CLI.
    Керує викликом автоскидання та завантаженням бінарних файлів у SPI Flash.
    """

    def __init__(self, port: str, baudrate: int = 115200):
        self.port = port
        self.baudrate = baudrate
        self.reset_ctrl = ESPResetController(port, baudrate)

    def flash_binary(self, binary_path: str, flash_address: str = "0x00000") -> bool:
        """
        Переводить ESP8266 у режим завантажувача та викликає esptool для запису прошивки.
        """
        print(f"[INFO] Спроба підключення до послідовного порту {self.port}...")

        try:
            # Виконуємо апаратний скид у режим UART Download
            print("[INFO] Формування сигналів DTR/RTS для переведення в UART Download Mode...")
            self.reset_ctrl.reset_to_bootloader()
            self.reset_ctrl.close() # Звільняємо порт для esptool

            time.sleep(0.1)

            # Формуємо команду виклику esptool
            cmd = [
                sys.executable, "-m", "esptool",
                "--port", self.port,
                "--baud", str(self.baudrate),
                "--chip", "esp8266",
                "write_flash",
                "--flash_mode", "dio",
                "--flash_size", "detect",
                flash_address, binary_path
            ]

            print(f"[INFO] Запуск утиліти esptool для запису файлу '{binary_path}' за адресою {flash_address}...")
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print("[УСПІХ] Прошивку успішно записано у SPI Flash!")
                print(result.stdout)

                # Після прошивання переводимо мікроконтролер у режим автономного старту
                print("[INFO] Виконання скидання для автономного запуску з Flash...")
                self.reset_ctrl.open()
                self.reset_ctrl.reset_to_app()
                self.reset_ctrl.close()
                print("[УСПІХ] ESP8266 успішно перезапущено у режим SPI Flash Boot!")
                return True
            else:
                print("[ПОМИЛКА] Збій під час виконання esptool:")
                print(result.stderr or result.stdout)
                return False

        except Exception as e:
            print(f"[ПОМИЛКА] Виняток під час процедури прошивання: {e}")
            return False
        finally:
            self.reset_ctrl.close()

def main():
    parser = argparse.ArgumentParser(
        description="Автоматизований скрипт прошивання ESP8266 через маніпуляцію DTR/RTS лініями UART"
    )
    parser.add_argument("-p", "--port", required=True, help="Послідовний порт (наприклад, COM3 або /dev/ttyUSB0)")
    parser.add_argument("-b", "--baud", type=int, default=115200, help="Швидкість UART (за замовчуванням: 115200)")
    parser.add_argument("-f", "--file", required=True, help="Шлях до бінарного файлу прошивки (.bin)")
    parser.add_argument("-a", "--addr", default="0x00000", help="Адреса Flash пам'яті (за замовчуванням: 0x00000)")

    args = parser.parse_args()

    flasher = ESPFlasher(args.port, args.baud)
    success = flasher.flash_binary(args.file, args.addr)

    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
