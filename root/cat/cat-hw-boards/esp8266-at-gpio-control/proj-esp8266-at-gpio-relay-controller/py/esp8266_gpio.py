"""Модуль для керування GPIO-виводами мікроконтролера ESP8266 через AT-команди."""

import time
from typing import Any, List, Union
import serial


class ESP8266GPIOError(Exception):
    """Кастомний виняток для обробки помилок взаємодії з ESP8266 (тайм-аути, відсутність відповіді, статус ERROR)."""

    pass


class ESP8266GPIOController:
    """Клас для керування GPIO виводами ESP8266 через послідовний порт (PySerial).

    Здійснює форматування AT-команд (AT+PINMODE, AT+PINWRITE, AT+PINREAD),
    полінійний/асинхронний розбір текстових відповідей UART, перевірку маркерів
    підтвердження OK/ERROR та генерацію винятків ESP8266GPIOError.
    """

    # Режими конфігурації GPIO виводів
    PIN_MODE_INPUT = 0
    PIN_MODE_OUTPUT = 1
    PIN_MODE_INPUT_PULLUP = 2

    # Логічні рівні сигналів
    LOW = 0
    HIGH = 1

    def __init__(
        self,
        port: Union[str, Any],
        baudrate: int = 115200,
        timeout: float = 2.0,
    ) -> None:
        """Ініціалізація об'єкта контролера ESP8266 GPIO.

        :param port: Назва послідовного порту (наприклад, 'COM3' або '/dev/ttyUSB0')
                     або вже відкритий екземпляр serial.Serial.
        :param baudrate: Швидкість передачі по UART (за замовчуванням 115200).
        :param timeout: Тайм-аут читання з порту в секундах.
        """
        if isinstance(port, str):
            try:
                self.serial = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)
            except serial.SerialException as err:
                raise ESP8266GPIOError(f"Не вдалося відкрити послідовний порт {port}: {err}") from err
            self._owns_serial = True
        else:
            self.serial = port
            self._owns_serial = False

    def close(self) -> None:
        """Закриття послідовного порту, якщо він був відкритий цим контролером."""
        if self._owns_serial and self.serial and hasattr(self.serial, "is_open") and self.serial.is_open:
            self.serial.close()

    def __enter__(self) -> "ESP8266GPIOController":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def send_at_command(self, command: str, timeout: float = 2.0) -> List[str]:
        """Форматує та надсилає AT-команду в послідовний порт UART.

        Виконує полінійний розбір текстових відповідей від мікроконтролера
        до отримання маркерів підтвердження OK або ERROR.

        :param command: Текст AT-команд без символів переведення рядка (наприклад, 'AT+PINMODE=4,1').
        :param timeout: Максимальний час очікування відповіді у секундах.
        :return: Список рядків текстової відповіді від модуля ESP8266 (без OK/ERROR).
        :raises ESP8266GPIOError: У разі отримання ERROR або виникнення тайм-ауту.
        """
        if not self.serial or (hasattr(self.serial, "is_open") and not self.serial.is_open):
            raise ESP8266GPIOError("Послідовний порт не відкритий або недоступний.")

        # Очищення вхідних та вихідних буферів перед відправкою інструкції
        if hasattr(self.serial, "reset_input_buffer"):
            self.serial.reset_input_buffer()
        if hasattr(self.serial, "reset_output_buffer"):
            self.serial.reset_output_buffer()

        full_cmd = f"{command}\r\n"
        try:
            self.serial.write(full_cmd.encode("ascii"))
            if hasattr(self.serial, "flush"):
                self.serial.flush()
        except Exception as err:
            raise ESP8266GPIOError(f"Помилка запису в послідовний порт UART: {err}") from err

        response_lines: List[str] = []
        start_time = time.time()
        status_ok = False

        while (time.time() - start_time) < timeout:
            in_waiting = getattr(self.serial, "in_waiting", 1)
            if in_waiting > 0:
                raw_line = self.serial.readline()
                try:
                    line = raw_line.decode("utf-8", errors="ignore").strip()
                except Exception:
                    continue

                if not line:
                    continue

                # Ігнорування луно-відповіді (echo) відправленої команди
                if line == command or line == full_cmd.strip():
                    continue

                if line == "OK":
                    status_ok = True
                    break
                elif line == "ERROR" or line.startswith("ERR"):
                    raise ESP8266GPIOError(
                        f"Модуль ESP8266 повернув статус помилки на команду '{command}': {line}"
                    )
                else:
                    response_lines.append(line)
            else:
                time.sleep(0.01)

        if not status_ok:
            raise ESP8266GPIOError(
                f"Тайм-аут ({timeout} с) очікування підтвердження OK від ESP8266 на команду: {command}"
            )

        return response_lines

    def test_connection(self) -> bool:
        """Перевірка зв'язку з модулем ESP8266 за допомогою базисної AT-команди.

        :return: True, якщо модуль успішно відповідає OK.
        """
        self.send_at_command("AT")
        return True

    def set_pin_mode(self, pin: int, mode: int) -> None:
        """Налаштування режиму роботи GPIO-виводу ESP8266 (AT+PINMODE).

        :param pin: Номер GPIO виводу (наприклад, 4, 5, 12, 13, 14).
        :param mode: Режим виводу (0 - INPUT, 1 - OUTPUT, 2 - INPUT_PULLUP).
        """
        if mode not in (self.PIN_MODE_INPUT, self.PIN_MODE_OUTPUT, self.PIN_MODE_INPUT_PULLUP):
            raise ValueError(
                f"Некоректний режим виводу {mode}. Очікується 0 (INPUT), 1 (OUTPUT) або 2 (INPUT_PULLUP)."
            )

        cmd = f"AT+PINMODE={pin},{mode}"
        self.send_at_command(cmd)

    def write_pin(self, pin: int, state: int) -> None:
        """Встановлення логічного стану на GPIO-виводі ESP8266 (AT+PINWRITE).

        :param pin: Номер GPIO виводу.
        :param state: Рівень сигналу (0 - LOW, 1 - HIGH).
        """
        val = 1 if state else 0
        cmd = f"AT+PINWRITE={pin},{val}"
        self.send_at_command(cmd)

    def read_pin(self, pin: int) -> int:
        """Зчитування фактичного логічного стану з GPIO-виводу ESP8266 (AT+PINREAD).

        :param pin: Номер GPIO виводу.
        :return: Логічний стан виводу (0 - LOW, 1 - HIGH).
        :raises ESP8266GPIOError: Якщо не вдалося розпарсити значення стану від модуля.
        """
        cmd = f"AT+PINREAD={pin}"
        lines = self.send_at_command(cmd)

        for line in lines:
            if line.startswith("+PINREAD:"):
                payload = line.split(":", 1)[1].strip()
                parts = [p.strip() for p in payload.split(",")]
                if len(parts) >= 2 and parts[1].isdigit():
                    return int(parts[1])
                elif len(parts) == 1 and parts[0].isdigit():
                    return int(parts[0])
            elif line.isdigit() and line in ("0", "1"):
                return int(line)

        raise ESP8266GPIOError(f"Не вдалося розпізнати значення стану виводу з відповіді ESP8266: {lines}")
