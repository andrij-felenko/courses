"""
serial_reader.py
Підключення до послідовного порту UART (PySerial), потокове зчитування
і розбір пакетів вимірювань 3D-вектора магнітного поля QMC5883L від мікроконтролера,
валідація даних та зворотна передача розрахованих калібрувальних коефіцієнтів.
"""
import json
import logging
import math
import random
import time
from typing import Dict, List, Optional, Tuple

import numpy as np
import serial

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class SerialReaderError(Exception):
    """Кастомний виняток для помилок підключення та парсингу послідовного порту."""
    pass


class SerialReader:
    """
    Клас для управління UART-з'єднанням із мікроконтролером,
    зчитування потокових вимірювань QMC5883L та відправки калібрувальних коефіцієнтів.
    """

    def __init__(
        self,
        port: str = "COM3",
        baudrate: int = 115200,
        timeout: float = 1.0,
        mock_mode: bool = False,
    ) -> None:
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.mock_mode = mock_mode
        self.serial_conn: Optional[serial.Serial] = None
        self.is_connected: bool = False
        self._mock_sample_counter: int = 0

    def connect(self) -> None:
        """Встановлює з'єднання з послідовним портом або активує симуляційний режим."""
        if self.mock_mode:
            self.is_connected = True
            logging.info("З'єднання ініціалізовано в симуляційному режимі (mock_mode=True).")
            return

        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
            )
            self.is_connected = True
            logging.info(f"Успішно підключено до послідовного порту {self.port} ({self.baudrate} baud).")
        except (serial.SerialException, OSError) as e:
            self.is_connected = False
            logging.warning(f"Не вдалося відкрити порт {self.port}: {e}. Перехід у симуляційний режим.")
            self.mock_mode = True
            self.is_connected = True

    def disconnect(self) -> None:
        """Безпечно закриває відкритий послідовний порт."""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            logging.info(f"Послідовний порт {self.port} закрито.")
        self.is_connected = False

    def _generate_mock_sample(self) -> Tuple[float, float, float]:
        """
        Генерує симульований 3D-вектор магнітного поля QMC5883L
        із заданим зсувом Hard-Iron та масшабуванням Soft-Iron.
        """
        self._mock_sample_counter += 1
        t = self._mock_sample_counter * 0.05
        phi = (t * 0.7) % (2 * math.pi)
        theta = (t * 0.3) % math.pi

        # Ідеальний вектор на одиничній сфері
        ux = math.sin(theta) * math.cos(phi)
        uy = math.sin(theta) * math.sin(phi)
        uz = math.cos(theta)

        # Справжні викривлення: Hard-Iron zsuv (150, -200, 50) та Soft-Iron matrix
        true_offset = np.array([150.0, -200.0, 50.0])
        true_soft_inv = np.array([
            [1.4, 0.15, 0.0],
            [0.15, 0.85, 0.1],
            [0.0, 0.1, 1.15]
        ])

        u = np.array([ux, uy, uz])
        raw = (true_soft_inv @ u) * 400.0 + true_offset
        noise = np.random.normal(0, 3.0, size=3)
        raw_noisy = raw + noise

        return float(raw_noisy[0]), float(raw_noisy[1]), float(raw_noisy[2])

    def parse_packet(self, line: str) -> Tuple[float, float, float]:
        """
        Розбирає рядок з UART.
        Підтримує JSON ({"x": 10, "y": 20, "z": 30}), CSV ("10,20,30") та префікс ("MAG:10,20,30").
        """
        line = line.strip()
        if not line:
            raise SerialReaderError("Отримано порожній рядок з UART.")

        try:
            if line.startswith("{") and line.endswith("}"):
                data = json.loads(line)
                return float(data["x"]), float(data["y"]), float(data["z"])

            if ":" in line:
                line = line.split(":", 1)[1].strip()

            parts = line.split(",")
            if len(parts) == 3:
                return float(parts[0]), float(parts[1]), float(parts[2])

            parts_space = line.split()
            if len(parts_space) == 3:
                return float(parts_space[0]), float(parts_space[1]), float(parts_space[2])

            raise SerialReaderError(f"Неможливо розпізнати формат пакету: '{line}'")
        except (ValueError, KeyError, json.JSONDecodeError) as e:
            raise SerialReaderError(f"Помилка парсингу пакета даних ('{line}'): {e}") from e

    def validate_sample(self, x: float, y: float, z: float) -> Tuple[float, float, float]:
        """
        Перевіряє діапазон вимірювань QMC5883L (зазвичай ±32768 LSB або ±8 Gauss).
        Відсіює NaN та нескінченні значення.
        """
        if math.isnan(x) or math.isnan(y) or math.isnan(z):
            raise SerialReaderError("Вибірка містить значення NaN.")
        if math.isinf(x) or math.isinf(y) or math.isinf(z):
            raise SerialReaderError("Вибірка містить нескінченні значення Inf.")

        max_limit = 32768.0
        if abs(x) > max_limit or abs(y) > max_limit or abs(z) > max_limit:
            raise SerialReaderError(f"Перевищення допустимого діапазону LSB: ({x}, {y}, {z})")

        return x, y, z

    def read_sample(self) -> Tuple[float, float, float]:
        """
        Зчитує один 3D-вектор з послідовного порту або симулятора,
        виконує розбір та перевірку цілісності.
        """
        if not self.is_connected:
            raise SerialReaderError("Немає активного з'єднання з UART.")

        if self.mock_mode:
            x, y, z = self._generate_mock_sample()
            time.sleep(0.01)
            return self.validate_sample(x, y, z)

        try:
            if not self.serial_conn:
                raise SerialReaderError("Об'єкт Serial не ініціалізовано.")

            raw_bytes = self.serial_conn.readline()
            if not raw_bytes:
                raise SerialReaderError("Таймаут читання з послідовного порту.")

            line = raw_bytes.decode("utf-8", errors="replace")
            x, y, z = self.parse_packet(line)
            return self.validate_sample(x, y, z)
        except serial.SerialException as e:
            raise SerialReaderError(f"Помилка введення/виведення UART: {e}") from e

    def send_calibration(
        self,
        hard_iron_offset: np.ndarray,
        soft_iron_matrix: np.ndarray,
    ) -> bool:
        """
        Формує та передає назад на мікроконтролер розраховані калібрувальні коефіцієнти.
        Пакує вектор Hard-Iron (bx, by, bz) та матрицю Soft-Iron (3x3) у JSON-структуру.
        """
        if not self.is_connected:
            raise SerialReaderError("Неможливо відправити дані: UART не підключено.")

        calib_payload = {
            "cmd": "SET_CALIBRATION",
            "hard_iron": [
                round(float(hard_iron_offset[0]), 4),
                round(float(hard_iron_offset[1]), 4),
                round(float(hard_iron_offset[2]), 4),
            ],
            "soft_iron": [
                [round(float(val), 6) for val in row]
                for row in soft_iron_matrix
            ],
        }

        json_cmd = json.dumps(calib_payload) + "\n"

        if self.mock_mode:
            logging.info(f"[MOCK UART SEND] Передано команду на МК: {json_cmd.strip()}")
            return True

        try:
            if self.serial_conn and self.serial_conn.is_open:
                self.serial_conn.write(json_cmd.encode("utf-8"))
                self.serial_conn.flush()
                logging.info(f"Калібрувальні коефіцієнти успішно відправлені на МК через {self.port}.")
                return True
            return False
        except serial.SerialException as e:
            raise SerialReaderError(f"Помилка запису в UART: {e}") from e
