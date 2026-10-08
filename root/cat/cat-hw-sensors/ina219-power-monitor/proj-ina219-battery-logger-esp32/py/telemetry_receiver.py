"""
telemetry_receiver.py
Приймач телеметрії INA219 через UART або мережевий сокет.
"""
import json
import logging
import socket
import time
from typing import Dict, List, Optional

import serial

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class TelemetryDataError(Exception):
    """
    Кастомний виняток для обробки помилок формату телеметрії,
    обривів зв'язку UART/мережі та виявлення аномальних вибірок.
    """
    pass


class TelemetryReceiver:
    """
    Клас для підключення до послідовного порту UART або мережевого з'єднання,
    потокового зчитування й розбору пакетів вимірювань INA219,
    фільтрації аномальних вибірок та автоматичного збереження часових рядів у CSV/JSON.
    """

    def __init__(
        self,
        connection_type: str = "uart",
        port_or_host: str = "COM3",
        baud_or_port: int = 115200,
        timeout: float = 2.0,
        voltage_min: float = 0.0,
        voltage_max: float = 30.0,
        current_max: float = 5000.0,
        power_max: float = 60000.0,
    ) -> None:
        self.connection_type = connection_type.lower()
        self.port_or_host = port_or_host
        self.baud_or_port = baud_or_port
        self.timeout = timeout

        self.voltage_min = voltage_min
        self.voltage_max = voltage_max
        self.current_max = current_max
        self.power_max = power_max

        self.serial_conn: Optional[serial.Serial] = None
        self.socket_conn: Optional[socket.socket] = None
        self.is_connected: bool = False

    def connect(self) -> None:
        """Встановлює з'єднання через UART або мережевий сокет."""
        try:
            if self.connection_type == "uart":
                self.serial_conn = serial.Serial(
                    port=self.port_or_host,
                    baudrate=self.baud_or_port,
                    timeout=self.timeout,
                )
                self.is_connected = True
                logging.info(f"Успішно підключено до UART порту {self.port_or_host} ({self.baud_or_port} baud)")
            elif self.connection_type == "network":
                self.socket_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket_conn.settimeout(self.timeout)
                self.socket_conn.connect((self.port_or_host, int(self.baud_or_port)))
                self.is_connected = True
                logging.info(f"Успішно підключено до сокета {self.port_or_host}:{self.baud_or_port}")
            elif self.connection_type == "mock":
                self.is_connected = True
                logging.info("Підключено в режимі симуляції (mock)")
            else:
                raise TelemetryDataError(f"Непідтримуваний тип з'єднання: {self.connection_type}")
        except (serial.SerialException, socket.error, OSError) as e:
            self.is_connected = False
            raise TelemetryDataError(f"Помилка підключення ({self.connection_type}): {e}") from e

    def disconnect(self) -> None:
        """Безпечно закриває відкриті з'єднання."""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            logging.info("UART з'єднання закрито.")
        if self.socket_conn:
            try:
                self.socket_conn.close()
                logging.info("Мережеве сокет-з'єднання закрито.")
            except Exception as e:
                logging.warning(f"Помилка при закритті сокета: {e}")
        self.is_connected = False

    def parse_telemetry_line(self, line: str) -> Dict[str, float]:
        """
        Розбирає рядок з телеметричними даними INA219.
        Підтримує формати JSON або CSV/key-value.
        Повертає словник із ключами: timestamp, v_bus, v_shunt_mv, current_ma, power_mw.
        """
        line = line.strip()
        if not line:
            raise TelemetryDataError("Отримано порожній рядок телеметрії")

        try:
            if line.startswith("{") and line.endswith("}"):
                data = json.loads(line)
                return {
                    "timestamp": float(data.get("timestamp", time.time())),
                    "v_bus": float(data["v_bus"]),
                    "v_shunt_mv": float(data.get("v_shunt_mv", 0.0)),
                    "current_ma": float(data["current_ma"]),
                    "power_mw": float(data["power_mw"]),
                }
            parts = line.split(",")
            if len(parts) >= 4:
                kv = {}
                is_kv = False
                for p in parts:
                    if "=" in p:
                        k, v = p.split("=", 1)
                        kv[k.strip()] = float(v.strip())
                        is_kv = True
                if is_kv:
                    return {
                        "timestamp": float(kv.get("timestamp", time.time())),
                        "v_bus": float(kv["v_bus"]),
                        "v_shunt_mv": float(kv.get("v_shunt_mv", 0.0)),
                        "current_ma": float(kv["current_ma"]),
                        "power_mw": float(kv["power_mw"]),
                    }

                if len(parts) == 5:
                    return {
                        "timestamp": float(parts[0]),
                        "v_bus": float(parts[1]),
                        "v_shunt_mv": float(parts[2]),
                        "current_ma": float(parts[3]),
                        "power_mw": float(parts[4]),
                    }
                return {
                    "timestamp": time.time(),
                    "v_bus": float(parts[0]),
                    "v_shunt_mv": float(parts[1]),
                    "current_ma": float(parts[2]),
                    "power_mw": float(parts[3]),
                }
            raise TelemetryDataError(f"Неможливо розібрати рядок телеметрії: '{line}'")
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            raise TelemetryDataError(f"Помилка розбору даних телеметрії ('{line}'): {e}") from e

    def validate_sample(self, sample: Dict[str, float]) -> Dict[str, float]:
        """
        Перевіряє коректність фізичних значень вибірки INA219.
        Відфільтровує від'ємні або аномально високі значення напруги, струму та потужності.
        """
        v_bus = sample.get("v_bus", 0.0)
        current_ma = sample.get("current_ma", 0.0)
        power_mw = sample.get("power_mw", 0.0)

        if not (self.voltage_min <= v_bus <= self.voltage_max):
            raise TelemetryDataError(
                f"Аномальне значення напруги шини: {v_bus} В (допустимо {self.voltage_min}..{self.voltage_max} В)"
            )
        if abs(current_ma) > self.current_max:
            raise TelemetryDataError(
                f"Аномальне значення струму: {current_ma} мА (макс {self.current_max} мА)"
            )
        if power_mw < 0 or power_mw > self.power_max:
            raise TelemetryDataError(
                f"Аномальне значення потужності: {power_mw} мВт (макс {self.power_max} мВт)"
            )

        return sample

    def read_sample(self) -> Dict[str, float]:
        """Зчитує один пакет телеметрії, розбирає його та перевіряє валідність."""
        if not self.is_connected:
            raise TelemetryDataError("Канал зв'язку не підключено")

        try:
            line = ""
            if self.connection_type == "uart":
                if not self.serial_conn:
                    raise TelemetryDataError("UART з'єднання втрачено")
                raw_bytes = self.serial_conn.readline()
                if not raw_bytes:
                    raise TelemetryDataError("Таймаут читання з UART")
                line = raw_bytes.decode("utf-8", errors="replace")
            elif self.connection_type == "network":
                if not self.socket_conn:
                    raise TelemetryDataError("Мережеве з'єднання втрачено")
                chunks = []
                while True:
                    char = self.socket_conn.recv(1)
                    if not char:
                        break
                    if char == b"\n":
                        break
                    chunks.append(char)
                if not chunks:
                    raise TelemetryDataError("Таймаут чи обрив сокета")
                line = b"".join(chunks).decode("utf-8", errors="replace")
            else:
                raise TelemetryDataError("Пряме читання викликане у режимі без активного джерела")

            sample = self.parse_telemetry_line(line)
            return self.validate_sample(sample)
        except (serial.SerialException, socket.error) as e:
            raise TelemetryDataError(f"Помилка введення/виведення під час читання: {e}") from e

    def save_to_csv(self, data: List[Dict[str, float]], filepath: str) -> None:
        """Зберігає список вибірок у CSV-файл."""
        if not data:
            logging.warning("Немає даних для збереження в CSV")
            return
        fieldnames = ["timestamp", "v_bus", "v_shunt_mv", "current_ma", "power_mw"]
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(",".join(fieldnames) + "\n")
            for item in data:
                row = [str(item.get(k, 0.0)) for k in fieldnames]
                f.write(",".join(row) + "\n")
        logging.info(f"Часовий ряд збережено у CSV-файл: {filepath} ({len(data)} записів)")

    def save_to_json(self, data: List[Dict[str, float]], filepath: str) -> None:
        """Зберігає список вибірок у JSON-файл."""
        if not data:
            logging.warning("Немає даних для збереження в JSON")
            return
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logging.info(f"Часовий ряд збережено у JSON-файл: {filepath} ({len(data)} записів)")

    def start_collection(
        self,
        duration_seconds: float,
        output_file: str,
        file_format: str = "csv",
        interval: float = 0.1,
        simulated_data: Optional[List[Dict[str, float]]] = None,
    ) -> List[Dict[str, float]]:
        """
        Збирає телеметрію протягом заданого часу або із переданого списку вибірок,
        фільтрує аномалії та зберігає результат у файл.
        """
        samples: List[Dict[str, float]] = []
        start_time = time.time()
        logging.info(f"Розпочато збір телеметрії (тривалість: {duration_seconds} с)...")

        if simulated_data is not None:
            for raw_sample in simulated_data:
                try:
                    valid = self.validate_sample(raw_sample)
                    samples.append(valid)
                except TelemetryDataError as err:
                    logging.warning(f"Пропущено аномальну вибірку: {err}")
        else:
            while (time.time() - start_time) < duration_seconds:
                try:
                    sample = self.read_sample()
                    samples.append(sample)
                except TelemetryDataError as err:
                    logging.warning(f"Помилка телеметрії: {err}")
                time.sleep(interval)

        if file_format.lower() == "csv":
            self.save_to_csv(samples, output_file)
        elif file_format.lower() == "json":
            self.save_to_json(samples, output_file)
        else:
            raise TelemetryDataError(f"Невідомий формат файлу для збереження: {file_format}")

        return samples
