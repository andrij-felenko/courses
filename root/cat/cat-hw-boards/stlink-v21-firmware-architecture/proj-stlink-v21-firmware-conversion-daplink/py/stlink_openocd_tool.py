"""
Модуль автоматизації взаємодії з програматором/зневаджувачем ST-Link V2.1 через OpenOCD.
Забезпечує керування станом мікроконтролера, зчитування дампів Flash-пам'яті,
аналіз таблиці векторів ARM Cortex-M, розрахунок контрольних сум та процедуру розблокування.
"""

import hashlib
import logging
import os
import socket
import struct
import subprocess
import sys
import time
import zlib
from typing import Any, Dict, List, Optional, Tuple

# Налаштування логування для відстеження процесів діагностики та зневадження
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("STLinkOpenOCD")


class OpenOCDError(Exception):
    """Базовий виняток для помилок взаємодії з OpenOCD."""
    pass


class OpenOCDTimeoutError(OpenOCDError):
    """Виняток у разі перевищення часу очікування відповіді від OpenOCD."""
    pass


class OpenOCDConnectionError(OpenOCDError):
    """Виняток у разі збоїв сокетного з'єднання з TCL-сервером OpenOCD."""
    pass


class FirmwareValidationError(Exception):
    """Виняток у разі виявлення пошкоджень або невалідної структури binary-дампа."""
    pass


class STLinkOpenOCDController:
    """
    Клас керування фоновим сервером OpenOCD та взаємодії через TCL-сокет.
    Підтримує виконання низькорівневих команд ST-Link V2.1 (reset, dump_image, unlock, mass_erase).
    """

    def __init__(
        self,
        config_files: Optional[List[str]] = None,
        host: str = "127.0.0.1",
        tcl_port: int = 6666,
        timeout: float = 10.0
    ):
        """
        Ініціалізує контролер OpenOCD.

        :param config_files: Список конфігураційних файлів OpenOCD (інтерфейс, таргет).
        :param host: Хост для підключення до TCL-сервера.
        :param tcl_port: Порт TCL-сервера OpenOCD.
        :param timeout: Таймаут мережевих операцій у секундах.
        """
        if config_files is None:
            # Типові конфігураційні файли для ST-Link V2.1 та STM32F1
            self.config_files = ["interface/stlink-v2-1.cfg", "target/stm32f1x.cfg"]
        else:
            self.config_files = config_files

        self.host = host
        self.tcl_port = tcl_port
        self.timeout = timeout
        self.process: Optional[subprocess.Popen] = None
        self.socket: Optional[socket.socket] = None

    def start_server(self) -> None:
        """
        Запускає фоновий процес OpenOCD із заданими конфігураційними файлами.
        """
        cmd = ["openocd"]
        for cfg in self.config_files:
            cmd.extend(["-f", cfg])
        cmd.extend(["-c", f"tcl_port {self.tcl_port}"])

        logger.info("Запуск сервера OpenOCD: %s", " ".join(cmd))
        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        except FileNotFoundError:
            raise OpenOCDError(
                "Виконуваний файл OpenOCD не знайдено у системній змінній PATH. "
                "Перевірте встановлення OpenOCD та налаштування оточення."
            )
        except Exception as e:
            raise OpenOCDError(f"Не вдалося запустити процес OpenOCD: {e}")

        # Очікуємо готовності TCL-сервера
        start_time = time.time()
        connected = False
        while time.time() - start_time < self.timeout:
            if self.process.poll() is not None:
                _, stderr_out = self.process.communicate()
                raise OpenOCDError(f"Процес OpenOCD несподівано завершився: {stderr_out.strip()}")
            try:
                test_sock = socket.create_connection((self.host, self.tcl_port), timeout=0.5)
                test_sock.close()
                connected = True
                break
            except (socket.error, ConnectionRefusedError):
                time.sleep(0.2)

        if not connected:
            self.stop_server()
            raise OpenOCDTimeoutError(
                f"Сервер OpenOCD не відкрив TCL-порт {self.tcl_port} протягом {self.timeout} сек."
            )

        logger.info("Сервер OpenOCD успішно запущено та підготовлено до з'єднання.")

    def stop_server(self) -> None:
        """Зупиняє фоновий процес OpenOCD та закриває сокетне з'єднання."""
        self.disconnect_tcl()

        if self.process is not None:
            logger.info("Завершення фонового процесу OpenOCD...")
            self.process.terminate()
            try:
                self.process.wait(timeout=3.0)
            except subprocess.TimeoutExpired:
                logger.warning("Процес OpenOCD не припинив роботу за таймаутом, виконується примусове знищення.")
                self.process.kill()
                self.process.wait()
            self.process = None
            logger.info("Процес OpenOCD зупинено.")

    def connect_tcl(self) -> None:
        """Встановлює мережеве TCL-з'єднання з OpenOCD."""
        if self.socket is not None:
            return

        try:
            logger.info("Підключення до TCL-сервера OpenOCD %s:%d...", self.host, self.tcl_port)
            self.socket = socket.create_connection((self.host, self.tcl_port), timeout=self.timeout)
        except Exception as e:
            raise OpenOCDConnectionError(f"Неможливо підключитися до TCL-сервера {self.host}:{self.tcl_port}: {e}")

    def disconnect_tcl(self) -> None:
        """Закриває сокетне з'єднання з TCL-сервером."""
        if self.socket is not None:
            try:
                self.socket.close()
            except Exception:
                pass
            self.socket = None
            logger.info("Сокетне з'єднання з TCL-сервером закрито.")

    def send_tcl_command(self, command: str) -> str:
        """
        Передає низькорівневу TCL-команду серверу OpenOCD та повертає відповідь.
        Згідно з протоколом OpenOCD TCL, команда завершується байтом 0x1A (EOF delimiter).

        :param command: Текст команди OpenOCD.
        :return: Строкова відповідь сервера.
        """
        if self.socket is None:
            self.connect_tcl()

        # Відправка команди з символом завершення 0x1A
        payload = command.strip().encode("utf-8") + b"\x1a"
        try:
            self.socket.sendall(payload)
        except Exception as e:
            self.disconnect_tcl()
            raise OpenOCDConnectionError(f"Помилка надсилання команди '{command}' через сокет: {e}")

        # Зчитування відповіді до появи розділювача 0x1A
        buffer = bytearray()
        start_time = time.time()
        while True:
            if time.time() - start_time > self.timeout:
                raise OpenOCDTimeoutError(f"Перевищено таймаут ({self.timeout}s) очікування відповіді на '{command}'.")

            try:
                chunk = self.socket.recv(4096)
            except socket.timeout:
                raise OpenOCDTimeoutError(f"Таймаут сокету під час зчитування відповіді на команду '{command}'.")
            except Exception as e:
                self.disconnect_tcl()
                raise OpenOCDConnectionError(f"Збій зчитання з сокету під час виконання '{command}': {e}")

            if not chunk:
                self.disconnect_tcl()
                raise OpenOCDConnectionError("З'єднання з TCL-сервером розірвано протилежною стороною.")

            if b"\x1a" in chunk:
                delim_pos = chunk.index(b"\x1a")
                buffer.extend(chunk[:delim_pos])
                break
            else:
                buffer.extend(chunk)

        response = buffer.decode("utf-8", errors="replace").strip()
        if "Error:" in response or "error" in response.lower():
            logger.warning("Отримано повідомлення про помилку від OpenOCD: %s", response)

        return response

    def reset_halt(self) -> str:
        """
        Надсилає команду скидання та зупинки ядра мікроконтролера (reset halt).
        """
        logger.info("Виконання скидання та зупинки процесора (reset halt)...")
        res = self.send_tcl_command("reset halt")
        logger.info("Результат виконання reset halt: %s", res)
        return res

    def dump_image(self, filename: str, address: int = 0x08000000, size: int = 0x10000) -> str:
        """
        Зчитує дамп Flash-пам'яті у бінарний файл.

        :param filename: Шлях до файлу для збереження.
        :param address: Початкова адреса зчитування Flash (за замовчуванням 0x08000000).
        :param size: Розмір дампа в байтах.
        :return: Шлях до збереженого файлу.
        """
        normalized_path = filename.replace("\\", "/")
        cmd = f"dump_image {normalized_path} 0x{address:08X} 0x{size:08X}"
        logger.info("Зчитування пам'яті за допомогою команди: %s", cmd)
        
        response = self.send_tcl_command(cmd)
        logger.info("Відповідь OpenOCD: %s", response)

        if not os.path.exists(filename):
            raise OpenOCDError(f"Файл дампа '{filename}' не було створено сервером OpenOCD.")

        actual_size = os.path.getsize(filename)
        if actual_size == 0:
            raise OpenOCDError(f"Файл дампа '{filename}' порожній (0 байт).")

        logger.info("Дамп успішно збережено у файл %s (розмір: %d байт).", filename, actual_size)
        return filename

    def mass_erase(self, target_family: str = "stm32f1x", bank: int = 0) -> str:
        """
        Виконує масове стирання Flash-пам'яті мікроконтролера.

        :param target_family: Сімейство мікроконтролера (наприклад, stm32f1x, stm32l4x).
        :param bank: Номер банку пам'яті.
        """
        cmd = f"{target_family} mass_erase {bank}"
        logger.info("Виконання масового стирання пам'яті: %s", cmd)
        try:
            response = self.send_tcl_command(cmd)
        except OpenOCDError as e:
            logger.warning("Спроба %s повернула помилку: %s. Виконується секторальне стирання...", cmd, e)
            response = self.send_tcl_command(f"flash erase_sector {bank} 0 last")

        logger.info("Результат масового стирання: %s", response)
        return response

    def unlock_target(self, target_family: str = "stm32f1x", bank: int = 0) -> str:
        """
        Знімає захист від читання/запису Flash-пам'яті.

        :param target_family: Сімейство мікроконтролера.
        :param bank: Номер банку пам'яті.
        """
        cmd = f"{target_family} unlock {bank}"
        logger.info("Спроба зняття захисту Flash: %s", cmd)
        try:
            response = self.send_tcl_command(cmd)
        except OpenOCDError as e:
            logger.warning("Спроба %s зазнала невдачі, застосовується універсальна команда захисту...", cmd)
            response = self.send_tcl_command(f"flash protect {bank} 0 last off")

        logger.info("Результат зняття захисту: %s", response)
        return response

    def unbrick_target(self, target_family: str = "stm32f1x", bank: int = 0) -> bool:
        """
        Повна покрокова процедура відновлення («unbrick») пристрою:
        1. Скидання та зупинка процесора (reset halt).
        2. Зняття захисту читання/запису (unlock).
        3. Масове стирання пошкодженої Flash-пам'яті (mass_erase).
        4. Повторна зупинка ядра для подальшого прошивання.
        """
        logger.info("==================================================")
        logger.info("ПОЧАТОК ПРОЦЕДУРИ ВІДНОВЛЕННЯ ПРИСТРОЮ (UNBRICK)")
        logger.info("==================================================")

        try:
            # 1. Зупинка ядра
            self.reset_halt()
            time.sleep(0.2)

            # 2. Зняття захисту
            self.unlock_target(target_family=target_family, bank=bank)
            time.sleep(0.2)

            # 3. Масове стирання
            self.mass_erase(target_family=target_family, bank=bank)
            time.sleep(0.2)

            # 4. Фінальне скидання
            self.reset_halt()
            logger.info("Процедуру unbrick успішно виконано.")
            return True
        except Exception as e:
            logger.error("Помилка під час виконання процедури unbrick: %s", e)
            raise OpenOCDError(f"Процедура unbrick завершилася з помилкою: {e}")


class FirmwareValidator:
    """
    Клас для валідації цілісності та верифікації структури binary-дампів прошивки ARM Cortex-M.
    """

    def __init__(
        self,
        ram_start: int = 0x20000000,
        ram_end: int = 0x20080000,
        flash_start: int = 0x08000000,
        flash_end: int = 0x08200000
    ):
        """
        Ініціалізує валідатор з межами RAM та Flash.

        :param ram_start: Початкова адреса SRAM (за замовчуванням 0x20000000).
        :param ram_end: Кінцева адреса SRAM.
        :param flash_start: Початкова адреса Flash (за замовчуванням 0x08000000).
        :param flash_end: Кінцева адреса Flash.
        """
        self.ram_start = ram_start
        self.ram_end = ram_end
        self.flash_start = flash_start
        self.flash_end = flash_end

    def calculate_crc32(self, data: bytes) -> int:
        """
        Обчислює контрольні суму CRC32 бінарних даних.
        """
        return zlib.crc32(data) & 0xFFFFFFFF

    def calculate_sha256(self, data: bytes) -> str:
        """
        Обчислює SHA-256 хеш бінарних даних у шестнадцятирічному форматі.
        """
        return hashlib.sha256(data).hexdigest()

    def parse_vector_table(self, data: bytes) -> Tuple[int, int]:
        """
        Витягує значення початкового Stack Pointer (MSP) та адреси Reset Handler
        з перших 8 байтів векторної таблиці ARM Cortex-M.

        :param data: Бінарний масив прошивки.
        :return: Кортеж (Initial Stack Pointer, Reset Handler Address).
        """
        if len(data) < 8:
            raise FirmwareValidationError(
                f"Розмір даних ({len(data)} байт) недостатній для аналізу таблиці векторів (мінімум 8 байт)."
            )
        sp, reset_handler = struct.unpack("<II", data[:8])
        return sp, reset_handler

    def validate_vector_table(self, data: bytes) -> Dict[str, Any]:
        """
        Перевіряє вектори ARM Cortex-M:
        - Stack Pointer має бути вирівняний по 4/8 байт і знаходитися всередині SRAM.
        - Reset Handler має містити біт Thumb (LSB = 1) і його адреса вказувати у Flash.

        :param data: Бінарний масив прошивки.
        :return: Словник з детальною інформацією про результати перевірки.
        """
        sp, reset_handler = self.parse_vector_table(data)
        reasons: List[str] = []
        is_valid = True

        # Перевірка Stack Pointer
        sp_aligned = (sp % 4 == 0)
        sp_in_ram = (self.ram_start <= sp <= self.ram_end)
        sp_valid = sp_aligned and sp_in_ram

        if not sp_aligned:
            reasons.append(f"Покажчик стеку (SP = 0x{sp:08X}) не вирівняний по межі 4 байти.")
            is_valid = False
        if not sp_in_ram:
            reasons.append(
                f"Покажчик стеку (SP = 0x{sp:08X}) виходить за межі RAM "
                f"(0x{self.ram_start:08X} - 0x{self.ram_end:08X})."
            )
            is_valid = False

        # Перевірка Reset Handler
        thumb_bit_set = (reset_handler & 1) == 1
        actual_handler = reset_handler & ~1
        handler_in_flash = (self.flash_start <= actual_handler <= self.flash_end)
        reset_handler_valid = thumb_bit_set and handler_in_flash

        if not thumb_bit_set:
            reasons.append(
                f"Вектор Reset Handler (0x{reset_handler:08X}) не має встановленого біта Thumb (LSB=1)."
            )
            is_valid = False
        if not handler_in_flash:
            reasons.append(
                f"Адреса обробника скидання (0x{actual_handler:08X}) виходить за межі Flash "
                f"(0x{self.flash_start:08X} - 0x{self.flash_end:08X})."
            )
            is_valid = False

        return {
            "is_valid": is_valid,
            "stack_pointer": f"0x{sp:08X}",
            "reset_handler": f"0x{reset_handler:08X}",
            "actual_reset_handler": f"0x{actual_handler:08X}",
            "sp_valid": sp_valid,
            "reset_handler_valid": reset_handler_valid,
            "reasons": reasons
        }

    def validate_file(self, filepath: str) -> Dict[str, Any]:
        """
        Зчитує файл дампа прошивки з диску та аналізує його цілісність.

        :param filepath: Шлях до binary-файлу дампа.
        :return: Звіт валідації.
        """
        if not os.path.exists(filepath):
            raise FirmwareValidationError(f"Файл дампа '{filepath}' не знайдено.")

        with open(filepath, "rb") as f:
            data = f.read()

        if len(data) == 0:
            raise FirmwareValidationError(f"Файл дампа '{filepath}' є порожнім.")

        crc32_val = self.calculate_crc32(data)
        sha256_val = self.calculate_sha256(data)
        vector_res = self.validate_vector_table(data)

        report = {
            "filepath": filepath,
            "file_size_bytes": len(data),
            "crc32": f"0x{crc32_val:08X}",
            "sha256": sha256_val,
            "is_valid": vector_res["is_valid"],
            "vector_table_analysis": vector_res
        }

        return report


def main() -> None:
    """
    Демонстраційний сценарій тестування роботи класів STLinkOpenOCDController та FirmwareValidator.
    """
    logger.info("=== Демонстраційний запуск інструментарію ST-Link V2.1 + OpenOCD ===")

    # 1. Створення тестового синтетичного дампа ARM Cortex-M для демонстрації валідації
    test_dump_file = "test_firmware_dump.bin"
    valid_sp = 0x20005000       # Валідний SP всередині SRAM
    valid_reset = 0x08000109    # Валідний Reset Handler у Flash з бітом Thumb (LSB=1)
    mock_payload = b"\x00" * 256

    # Пакетуємо перші 8 байт (векторну таблицю) + заповнення
    header = struct.pack("<II", valid_sp, valid_reset)
    sample_firmware = header + mock_payload

    with open(test_dump_file, "wb") as f:
        f.write(sample_firmware)

    logger.info("Створено мок-файл прошивки: %s (%d байт)", test_dump_file, len(sample_firmware))

    # 2. Перевірка дампа за допомогою FirmwareValidator
    validator = FirmwareValidator(
        ram_start=0x20000000,
        ram_end=0x20020000,
        flash_start=0x08000000,
        flash_end=0x08080000
    )

    try:
        report = validator.validate_file(test_dump_file)
        logger.info("Результати валідації тестового дампа:")
        logger.info(" - Розмір файлу: %d байт", report["file_size_bytes"])
        logger.info(" - CRC32: %s", report["crc32"])
        logger.info(" - SHA-256: %s", report["sha256"])
        logger.info(" - Валідність векторної таблиці: %s", report["is_valid"])
        logger.info(" - SP: %s", report["vector_table_analysis"]["stack_pointer"])
        logger.info(" - Reset Handler: %s", report["vector_table_analysis"]["reset_handler"])
    except FirmwareValidationError as e:
        logger.error("Помилка валідації: %s", e)

    # 3. Демонстрація роботи з STLinkOpenOCDController
    controller = STLinkOpenOCDController(
        config_files=["interface/stlink-v2-1.cfg", "target/stm32f1x.cfg"],
        host="127.0.0.1",
        tcl_port=6666,
        timeout=3.0
    )

    logger.info("Спроба автономного підключення до OpenOCD сервера...")
    try:
        # Спроба підключитися до вже запущеного OpenOCD сервера або запустити новий
        controller.connect_tcl()
        logger.info("Успішне підключення до існуючого OpenOCD TCL-сервера.")
    except OpenOCDConnectionError:
        logger.info("Існуючого OpenOCD сервера не виявлено. Спроба локального запуску OpenOCD...")
        try:
            controller.start_server()
            controller.connect_tcl()
        except OpenOCDError as e:
            logger.warning(
                "Запуск OpenOCD сервера пропущено (OpenOCD або пристрій ST-Link не виявлені у даному середовищі): %s", e
            )
            logger.info("Очищення тимчасових файлів тестування...")
            if os.path.exists(test_dump_file):
                os.remove(test_dump_file)
            return

    # Якщо OpenOCD доступний, виконуємо діагностичні та відновлювальні процедури
    try:
        controller.reset_halt()
        dumped_file = controller.dump_image("stlink_readout.bin", address=0x08000000, size=0x4000)
        dump_report = validator.validate_file(dumped_file)
        logger.info("Прочитаний з пристрою дамп є валідним: %s", dump_report["is_valid"])

        # Виконання unbrick за потреби
        controller.unbrick_target(target_family="stm32f1x")

    except OpenOCDError as e:
        logger.error("Виникла помилка під час виконання команд OpenOCD: %s", e)
    finally:
        controller.stop_server()
        if os.path.exists(test_dump_file):
            os.remove(test_dump_file)


if __name__ == "__main__":
    main()
