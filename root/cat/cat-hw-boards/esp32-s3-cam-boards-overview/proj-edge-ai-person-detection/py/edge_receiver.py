"""
Модуль для прийому потокового відео та телеметрії з Edge AI пристроїв на базі ESP32-S3.
Підтримує передачу даних через мережевий інтерфейс Wi-Fi (HTTP MJPEG/JSON)
та послідовний порт UART (PySerial).
"""

import json
import logging
import socket
import time
import urllib.request
import zlib
from typing import Dict, Optional, Tuple, Union

try:
    import serial
except ImportError:
    serial = None

logger = logging.getLogger(__name__)


class TelemetryParseError(Exception):
    """Кастомний виняток для обробки помилок парсингу телеметрії.
    
    Виникає при обривах з'єднання Wi-Fi/UART, пошкодженні бінарних або JSON пакетів
    детекції, розбіжності контрольних сум (CRC) та перевищенні часових тайм-аутів.
    """
    pass


class EdgeReceiver:
    """Клас для інкапсуляції зв'язку з платою відеозахоплення ESP32-S3.
    
    Забезпечує підключення через Wi-Fi (HTTP-потік) або послідовний порт UART (PySerial),
    прийом потокових JPEG-кадрів і телеметрії детекції, валідацію цілісності пакетів
    та розбір структур даних результатів нейромережевого інференсу.
    """

    MAGIC_HEADER = b"\xaa\x55"  # Сигнатура початку пакета UART
    MAX_PAYLOAD_SIZE = 10 * 1024 * 1024  # 10 МБ максимальний розмір кадру

    def __init__(
        self,
        mode: str = "wifi",
        host: str = "192.168.1.100",
        port: int = 8080,
        stream_path: str = "/stream",
        serial_port: str = "COM3",
        baudrate: int = 115200,
        timeout: float = 3.0,
    ) -> None:
        """Ініціалізація параметрів приймача даних з ESP32-S3.

        :param mode: Режим підключення ('wifi' або 'uart').
        :param host: IP-адреса або хост пристрою ESP32-S3 в мережі Wi-Fi.
        :param port: Мережевий порт HTTP сервака ESP32-S3.
        :param stream_path: URL-шлях до відеопотоку HTTP.
        :param serial_port: Назва послідовного порту UART (наприклад, 'COM3' або '/dev/ttyUSB0').
        :param baudrate: Швидкість передачі по UART (за замовчуванням 115200).
        :param timeout: Тайм-аут з'єднання та читання в секундах.
        """
        if mode not in ("wifi", "uart"):
            raise ValueError(f"Непідтримуваний режим підключення '{mode}'. Допустимі: 'wifi', 'uart'.")

        self.mode = mode
        self.host = host
        self.port = port
        self.stream_path = stream_path
        self.serial_port = serial_port
        self.baudrate = baudrate
        self.timeout = timeout

        self._http_response = None
        self._serial_conn = None
        self._is_connected = False

    def connect(self) -> None:
        """Встановлення з'єднання з платою ESP32-S3 відповідно до обраного режиму."""
        if self._is_connected:
            return

        if self.mode == "wifi":
            url = f"http://{self.host}:{self.port}{self.stream_path}"
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "ESP32S3-EdgeAI-Client/1.0"})
                self._http_response = urllib.request.urlopen(req, timeout=self.timeout)
                self._is_connected = True
                logger.info(f"Успішне підключення до Wi-Fi відеопотоку ESP32-S3: {url}")
            except Exception as err:
                raise TelemetryParseError(f"Не вдалося підключитися до Wi-Fi потоку {url}: {err}") from err

        elif self.mode == "uart":
            if serial is None:
                raise TelemetryParseError("Модуль 'pyserial' не встановлено. Встановіть його через 'pip install pyserial'.")
            try:
                self._serial_conn = serial.Serial(
                    port=self.serial_port,
                    baudrate=self.baudrate,
                    timeout=self.timeout,
                )
                self._is_connected = True
                logger.info(f"Успішно відкрито послідовний порт UART {self.serial_port} на швидкості {self.baudrate}")
            except serial.SerialException as err:
                raise TelemetryParseError(f"Помилка відкриття послідовного порту UART {self.serial_port}: {err}") from err

    def disconnect(self) -> None:
        """Завершення з'єднання та звільнення системних ресурсів."""
        if self._http_response:
            try:
                self._http_response.close()
            except Exception as err:
                logger.warning(f"Помилка при закритті HTTP з'єднання: {err}")
            self._http_response = None

        if self._serial_conn:
            try:
                if self._serial_conn.is_open:
                    self._serial_conn.close()
            except Exception as err:
                logger.warning(f"Помилка при закритті послідовного порту UART: {err}")
            self._serial_conn = None

        self._is_connected = False
        logger.info("З'єднання з ESP32-S3 успішно закрито.")

    def read_frame(self) -> Tuple[bytes, Dict]:
        """Прийом одного відеокадру JPEG та супутніх метаданих детекції.

        :return: Кортеж з (байтовий масив JPEG, словник метаданих детекції).
        :raises TelemetryParseError: При помилці парсингу, обриві з'єднання або перевищенні тайм-ауту.
        """
        if not self._is_connected:
            self.connect()

        if self.mode == "wifi":
            return self._read_wifi_frame()
        else:
            return self._read_uart_frame()

    def _read_wifi_frame(self) -> Tuple[bytes, Dict]:
        """Розбір одного кадру з HTTP MJPEG/Multipart потоку."""
        if not self._http_response:
            raise TelemetryParseError("HTTP-потік недоступний або з'єднання розірвано.")

        try:
            buffer = bytearray()
            start_time = time.time()

            while True:
                if time.time() - start_time > self.timeout:
                    raise TelemetryParseError("Перевищено тайм-аут очікування початку JPEG кадру з Wi-Fi.")

                chunk = self._http_response.read(4096)
                if not chunk:
                    raise TelemetryParseError("Потік даних Wi-Fi перервано сервером ESP32-S3.")

                buffer.extend(chunk)

                jpeg_start = buffer.find(b"\xff\xd8")
                if jpeg_start != -1:
                    prefix = buffer[:jpeg_start].decode("utf-8", errors="ignore")
                    metadata = self._extract_json_from_http_headers(prefix)

                    jpeg_end = buffer.find(b"\xff\xd9", jpeg_start)
                    while jpeg_end == -1:
                        if time.time() - start_time > self.timeout:
                            raise TelemetryParseError("Перевищено тайм-аут очікування кінця JPEG кадру.")
                        more = self._http_response.read(4096)
                        if not more:
                            raise TelemetryParseError("Неповний JPEG кадр у потоці Wi-Fi.")
                        buffer.extend(more)
                        jpeg_end = buffer.find(b"\xff\xd9", jpeg_start)

                    jpeg_bytes = bytes(buffer[jpeg_start : jpeg_end + 2])

                    if not metadata or not metadata.get("detections"):
                        default_meta = self._parse_default_telemetry()
                        default_meta.update(metadata)
                        metadata = default_meta

                    metadata["receive_timestamp_ms"] = time.time() * 1000.0
                    return jpeg_bytes, metadata

        except TelemetryParseError:
            raise
        except Exception as err:
            raise TelemetryParseError(f"Помилка зчитування відеокадру з Wi-Fi: {err}") from err

    def _read_uart_frame(self) -> Tuple[bytes, Dict]:
        """Зчитування та валідація бінарного пакета кадру й метаданих через UART.

        Структура бінарного пакета ESP32-S3 UART:
        [2B Magic 0xAA55] [4B Telemetry Len] [4B JPEG Len] [4B CRC32] [N B JSON Telemetry] [M B JPEG Image]
        """
        if not self._serial_conn or not self._serial_conn.is_open:
            raise TelemetryParseError("Послідовний порт UART не відкритий.")

        try:
            start_time = time.time()
            while True:
                if time.time() - start_time > self.timeout:
                    raise TelemetryParseError("Тайм-аут очікування сигнатури пакета UART (0xAA55).")

                header_byte = self._serial_conn.read(1)
                if not header_byte:
                    continue
                if header_byte == b"\xaa":
                    next_byte = self._serial_conn.read(1)
                    if next_byte == b"\x55":
                        break

            meta_header = self._read_exact_uart(12)
            json_len = int.from_bytes(meta_header[0:4], byteorder="big")
            jpeg_len = int.from_bytes(meta_header[4:8], byteorder="big")
            expected_crc = int.from_bytes(meta_header[8:12], byteorder="big")

            if json_len > 1024 * 1024 or jpeg_len > self.MAX_PAYLOAD_SIZE:
                raise TelemetryParseError(f"Неприпустимі розміри корисного навантаження UART: json_len={json_len}, jpeg_len={jpeg_len}.")

            payload = self._read_exact_uart(json_len + jpeg_len)

            actual_crc = zlib.crc32(payload) & 0xFFFFFFFF
            if actual_crc != expected_crc:
                raise TelemetryParseError(
                    f"Помилка контрольної суми CRC32 пакета UART: отримано 0x{actual_crc:08X}, очікувалося 0x{expected_crc:08X}."
                )

            json_bytes = payload[:json_len]
            jpeg_bytes = payload[json_len:]

            if not (jpeg_bytes.startswith(b"\xff\xd8") and jpeg_bytes.endswith(b"\xff\xd9")):
                raise TelemetryParseError("Пошкоджений JPEG файл у пакеті UART (відсутні маркери SOI/EOI).")

            metadata = self._parse_telemetry(json_bytes)
            metadata["receive_timestamp_ms"] = time.time() * 1000.0

            return jpeg_bytes, metadata

        except TelemetryParseError:
            raise
        except Exception as err:
            raise TelemetryParseError(f"Збій зчитування пакета через UART: {err}") from err

    def _read_exact_uart(self, num_bytes: int) -> bytes:
        """Зчитування точної кількості байтів з UART з урахуванням тайм-ауту."""
        buf = bytearray()
        start_time = time.time()
        while len(buf) < num_bytes:
            if time.time() - start_time > self.timeout:
                raise TelemetryParseError(f"Тайм-аут зчитування {num_bytes} байтів з UART. Отримано лише {len(buf)} байтів.")
            chunk = self._serial_conn.read(num_bytes - len(buf))
            if chunk:
                buf.extend(chunk)
        return bytes(buf)

    def _extract_json_from_http_headers(self, header_text: str) -> Dict:
        """Вилучення та розбір JSON телеметрії із HTTP-заголовків або префіксу multipart."""
        metadata = self._parse_default_telemetry()
        for line in header_text.splitlines():
            if line.lower().startswith("x-telemetry-json:"):
                json_str = line.split(":", 1)[1].strip()
                try:
                    metadata.update(json.loads(json_str))
                except json.JSONDecodeError as err:
                    raise TelemetryParseError(f"Некоректний формат JSON у HTTP-заголовку: {err}") from err
            elif line.lower().startswith("x-inference-ms:"):
                try:
                    metadata["inference_ms"] = float(line.split(":", 1)[1].strip())
                except ValueError:
                    pass
        return metadata

    def _parse_telemetry(self, raw_json: bytes) -> Dict:
        """Валідація та парсинг JSON метаданих телеметрії детекції."""
        try:
            data = json.loads(raw_json.decode("utf-8"))
            if not isinstance(data, dict):
                raise TelemetryParseError("Метадані телеметрії повинні бути JSON-об'єктом (dict).")

            telemetry = {
                "timestamp_ms": float(data.get("timestamp_ms", time.time() * 1000.0)),
                "inference_ms": float(data.get("inference_ms", 0.0)),
                "send_timestamp_ms": float(data.get("send_timestamp_ms", time.time() * 1000.0)),
                "detections": [],
            }

            raw_detections = data.get("detections", [])
            if isinstance(raw_detections, list):
                for det in raw_detections:
                    if isinstance(det, dict) and "bbox" in det:
                        telemetry["detections"].append({
                            "class_id": int(det.get("class_id", 0)),
                            "label": str(det.get("label", f"class_{det.get('class_id', 0)}")),
                            "confidence": float(det.get("confidence", 0.0)),
                            "bbox": [float(c) for c in det["bbox"]],
                        })

            return telemetry
        except json.JSONDecodeError as err:
            raise TelemetryParseError(f"Помилка синтаксичного розбору JSON телеметрії: {err}") from err

    def _parse_default_telemetry(self) -> Dict:
        """Формування базової структури метаданих за відсутності додаткових даних."""
        now_ms = time.time() * 1000.0
        return {
            "timestamp_ms": now_ms,
            "inference_ms": 0.0,
            "send_timestamp_ms": now_ms,
            "detections": [],
        }

    def __enter__(self) -> "EdgeReceiver":
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.disconnect()
