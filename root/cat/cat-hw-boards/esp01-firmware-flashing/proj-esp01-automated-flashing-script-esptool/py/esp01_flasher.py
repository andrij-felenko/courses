#!/usr/bin/env python3
"""
Скрипт для автоматизованого керування прошиванням модулів ESP-01 через утиліту esptool.
Забезпечує формування команд, виклик через subprocess, контроль таймаутів та аналіз логів.
"""

import sys
import subprocess
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class FlashResult:
    """Структурований результат виконання команди esptool."""
    success: bool
    command: str
    return_code: int
    output: str
    error_message: Optional[str] = None


class ESP8266Flasher:
    """
    Клас для обгортки системного виклику консольної утиліти esptool.
    Дозволяє зчитувати ID чипа, прати флеш-пам'ять та записувати бінарні образи.
    """

    def __init__(self, port: str = "COM3", baudrate: int = 115200, esptool_path: str = "esptool.py"):
        self.port = port
        self.baudrate = baudrate
        self.esptool_path = esptool_path

    def _build_base_cmd(self) -> List[str]:
        """Формує базову команду запуску esptool із вказівкою порту та швидкості."""
        return [
            sys.executable, "-m", "esptool",
            "--port", self.port,
            "--baud", str(self.baudrate),
            "--chip", "esp8266",
        ]

    def _run_esptool(self, args: List[str], timeout: float = 30.0) -> FlashResult:
        """
        Виконує команду esptool через subprocess.run із контролем таймауту та обробкою винятків.
        """
        cmd = self._build_base_cmd() + args
        cmd_str = " ".join(cmd)

        try:
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=True
            )
            return FlashResult(
                success=True,
                command=cmd_str,
                return_code=process.returncode,
                output=process.stdout
            )

        except subprocess.TimeoutExpired as exc:
            output_so_far = (exc.stdout or "") + "\n" + (exc.stderr or "")
            return FlashResult(
                success=False,
                command=cmd_str,
                return_code=-1,
                output=output_so_far,
                error_message=f"Перевищено таймаут виконання ({timeout} сек)"
            )

        except subprocess.CalledProcessError as exc:
            return FlashResult(
                success=False,
                command=cmd_str,
                return_code=exc.returncode,
                output=exc.stdout or "",
                error_message=exc.stderr or "Помилка виконання команди esptool"
            )

        except FileNotFoundError:
            return FlashResult(
                success=False,
                command=cmd_str,
                return_code=-1,
                output="",
                error_message=f"Утиліту esptool не знайдено за шляхом '{self.esptool_path}'"
            )

    def get_chip_info(self) -> FlashResult:
        """Зчитує ідентифікаційні дані чипа ESP8266 (chip_id)."""
        return self._run_esptool(["chip_id"], timeout=10.0)

    def erase_flash(self) -> FlashResult:
        """Повністю стирає флеш-пам'ять модуля ESP-01."""
        return self._run_esptool(["erase_flash"], timeout=20.0)

    def write_flash(self, firmware_path: str, address: int = 0x00000, mode: str = "dout") -> FlashResult:
        """
        Записує бінарний образ прошивки у флеш-пам'ять за вказаною адресою.
        """
        addr_str = f"0x{address:05x}"
        args = [
            "write_flash",
            "--flash_mode", mode,
            addr_str, firmware_path
        ]
        return self._run_esptool(args, timeout=60.0)


def main():
    """Демонстрація використання класу ESP8266Flasher."""
    port_name = "COM3"
    print(f"=== Ініціалізація програмування ESP-01 на порту {port_name} ===")

    flasher = ESP8266Flasher(port=port_name, baudrate=115200)

    # 1. Читання інформації про чип
    print("\n[1/3] Перевірка підключення та зчитування Chip ID...")
    res_info = flasher.get_chip_info()
    if res_info.success:
        print("Успішно прочитано дані чипа:")
        print(res_info.output.strip())
    else:
        print(f"Помилка зчитування Chip ID: {res_info.error_message}")
        if res_info.output:
            print(f"Вивід esptool:\n{res_info.output}")

    # 2. Очищення пам'яті
    print("\n[2/3] Очищення флеш-пам'яті (erase_flash)...")
    res_erase = flasher.erase_flash()
    if res_erase.success:
        print("Повне стирання пам'яті пройшло успішно.")
    else:
        print(f"Помилка стирання пам'яті: {res_erase.error_message}")

    # 3. Запис прошивки
    firmware_file = "firmware.bin"
    print(f"\n[3/3] Прошивання образу '{firmware_file}'...")
    res_write = flasher.write_flash(firmware_path=firmware_file, address=0x00000)
    if res_write.success:
        print("Прошивання завершено успішно!")
    else:
        print(f"Помилка запису прошивки: {res_write.error_message}")


if __name__ == "__main__":
    main()
