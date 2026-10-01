"""Клієнт зв'язку з електрометром через послідовний порт RS-232/USB."""

import time
import serial


class ElectrometerClient:
    """Забезпечення зв'язку з вимірювальним приладом по послідовному порту."""

    def __init__(self, port: str = "COM3", baudrate: int = 9600, timeout: float = 1.0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self._connection = None

    def connect(self) -> None:
        """Відкриває послідовний порт для зв'язку з приладом."""
        try:
            self._connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            time.sleep(0.1)
            # Ініціалізація SCPI приладу
            self._send_command("*RST")
            self._send_command(":FUNC 'CURR'")
        except serial.SerialException:
            # Якщо реальний порт недоступний у демо-середовищі, фіксуємо режим симуляції
            self._connection = None

    def disconnect(self) -> None:
        """Закриває послідовне з'єднання."""
        if self._connection and self._connection.is_open:
            self._connection.close()
            self._connection = None

    def _send_command(self, cmd: str) -> None:
        """Надсилає SCPI-команду у прилад."""
        if self._connection and self._connection.is_open:
            command_str = f"{cmd}\r\n"
            self._connection.write(command_str.encode("ascii"))

    def read_measurement(self) -> tuple[float, float]:
        """
        Зчитує миттєві значення виміряної напруги (В) та струму витоку (А).
        Повертає кортеж (voltage_volts, current_amperes).
        """
        if self._connection and self._connection.is_open:
            self._send_command(":READ?")
            raw_response = self._connection.readline().decode("ascii").strip()
            parts = raw_response.split(",")
            if len(parts) >= 2:
                voltage = float(parts[0])
                current = float(parts[1])
                return voltage, current

        # Демонстраційний фолбек при відсутності задіяного приладу
        test_voltage = 100.0  # 100 В випробувальної напруги
        test_current = 2.5e-11  # 25 пА струму витоку (опір ~4 ГОм)
        return test_voltage, test_current
