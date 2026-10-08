"""Модуль для клієнтської взаємодії з ESP-модулями через командний інтерфейс ESP-AT."""

import time
from typing import Any, List, Optional, Union
import serial


class ESPATError(Exception):
    """Кастомний виняток для обробки помилок послідовного з'єднання,

    перевищення тайм-ауту очікування відповіді або виявлення статусів ERROR/FAIL
    від ESP-модуля.
    """

    pass


class ESPATClient:
    """Клас для інкапсуляції з'єднання PySerial та обміну AT-командами з ESP-модулем.

    Забезпечує форматування команд із термінацією \r\n, по-рядковий розбір
    вхідного текстового потоку UART, перевірку термінальних статусів OK/ERROR,
    виконання діагностичних запитів та динамічне переналаштування UART.
    """

    def __init__(
        self,
        port: Union[str, Any],
        baudrate: int = 115200,
        timeout: float = 2.0,
    ) -> None:
        """Ініціалізація клієнта ESP-AT та налаштування послідовного порту UART.

        :param port: Назва послідовного порту (наприклад, 'COM3' або '/dev/ttyUSB0')
                     або вже відкритий об'єкт serial.Serial.
        :param baudrate: Швидкість обміну даними UART у бодах (за замовчуванням 115200).
        :param timeout: Тайм-аут зчитування з порту в секундах (за замовчуванням 2.0).
        """
        if isinstance(port, str):
            try:
                self.serial = serial.Serial(
                    port=port,
                    baudrate=baudrate,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    timeout=timeout,
                )
            except serial.SerialException as err:
                raise ESPATError(
                    f"Не вдалося відкрити послідовний порт '{port}': {err}"
                ) from err
            self._owns_serial = True
        else:
            self.serial = port
            self._owns_serial = False

    def close(self) -> None:
        """Закриття послідовного порту, якщо він належить даному об'єкту."""
        if self._owns_serial and self.serial and hasattr(self.serial, "is_open") and self.serial.is_open:
            self.serial.close()

    def __enter__(self) -> "ESPATClient":
        """Підтримка протоколу контекстного менеджера."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Автоматичне закриття порту при виході з блоку with."""
        self.close()

    def send_command(
        self,
        command: str,
        timeout: Optional[float] = None,
    ) -> List[str]:
        """Форматування та відправка AT-команди з по-рядковим розбором відповіді UART.

        :param command: Текст AT-команди (наприклад, 'AT' або 'AT+GMR').
        :param timeout: Опціональний індивідуальний тайм-аут виконання в секундах.
        :return: Список текстових рядків відповіді трансівера (без термінального OK).
        :raises ESPATError: При виникненні тайм-ауту або отриманні статусу ERROR/FAIL.
        """
        if not self.serial or not self.serial.is_open:
            raise ESPATError("Послідовний порт UART не відкритий.")

        # Очищення вхідного буфера перед відправкою нової команди
        self.serial.reset_input_buffer()

        # Форматування AT-команди з обов'язковою термінацією \r\n за протоколом ESP-AT
        formatted_cmd = command.strip() + "\r\n"
        cmd_bytes = formatted_cmd.encode("ascii")

        # Тимчасова зміна тайм-ауту порту, якщо задано індивідуальне значення
        original_timeout = self.serial.timeout
        if timeout is not None:
            self.serial.timeout = timeout

        try:
            self.serial.write(cmd_bytes)
            self.serial.flush()

            response_lines: List[str] = []
            start_time = time.time()
            effective_timeout = timeout if timeout is not None else (original_timeout or 2.0)

            while True:
                line_bytes = self.serial.readline()
                if not line_bytes:
                    # Перевірка перевищення загального часу очікування відповіді
                    if time.time() - start_time >= effective_timeout:
                        raise ESPATError(
                            f"Перевищено тайм-аут ({effective_timeout} с) очікування "
                            f"відповіді на команду '{command}'."
                        )
                    continue

                line_str = line_bytes.decode("utf-8", errors="replace").strip("\r\n")

                # Пропускаємо порожні рядки та ехо самої команди, якщо воно увімкнене (ATE1)
                if not line_str or line_str == command.strip():
                    continue

                # Перевірка термінальних статусів виконання AT-команди
                if line_str == "OK":
                    return response_lines
                elif line_str in ("ERROR", "FAIL"):
                    details = " | ".join(response_lines) if response_lines else "немає додаткових даних"
                    raise ESPATError(
                        f"Команда '{command}' завершилася помилкою модуля [{line_str}]. Деталі: {details}"
                    )
                else:
                    response_lines.append(line_str)
        finally:
            # Відновлення початкового значення тайм-ауту
            if timeout is not None:
                self.serial.timeout = original_timeout

    def test_at(self) -> bool:
        """Перевірка наявності зв'язку з ESP-модулем (первинна діагностика).

        :return: True, якщо модуль успішно відповів OK на команду AT.
        """
        self.send_command("AT")
        return True

    def get_system_info(self) -> List[str]:
        """Зчитування системної інформації та версії прошивки модуля (команда AT+GMR).

        :return: Список рядків із детальною інформацією про версії AT, SDK та дату збірки.
        """
        return self.send_command("AT+GMR")

    def change_uart_config(
        self,
        baudrate: int,
        databits: int = 8,
        stopbits: int = 1,
        parity: int = 0,
        flow_control: int = 0,
    ) -> bool:
        """Динамічне переналаштування параметрів UART-порту трансівера (AT+UART_CUR).

        Параметри командного інтерфейсу ESP-AT:
        - databits: 5=5 bits, 6=6 bits, 7=7 bits, 8=8 bits
        - stopbits: 1=1 bit, 2=2 bits, 3=1.5 bits
        - parity: 0=None, 1=Odd, 2=Even
        - flow_control: 0=None, 1=RTS, 2=CTS, 3=RTS&CTS

        :param baudrate: Нова швидкість обміну у бодах (наприклад, 9600 або 115200).
        :param databits: Кількість біт даних у кадрі.
        :param stopbits: Кількість стоп-бітів.
        :param parity: Біт парності.
        :param flow_control: Апаратне керування потоком.
        :return: True, якщо конфігурація успішно змінена та зв'язок оновлено.
        """
        cmd = f"AT+UART_CUR={baudrate},{databits},{stopbits},{parity},{flow_control}"

        # Відправка команди AT+UART_CUR на поточній швидкості
        self.send_command(cmd)

        # Невелика пауза для завершення обробки команди мікроконтролером ESP
        time.sleep(0.1)

        # Програмне оновлення швидкості порту на боці PySerial
        self.serial.baudrate = baudrate
        self.serial.reset_input_buffer()
        time.sleep(0.1)

        return True
