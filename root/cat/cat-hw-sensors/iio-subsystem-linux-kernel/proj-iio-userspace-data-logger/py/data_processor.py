"""Модуль обробки сирих вимірювальних даних IIO за допомогою NumPy."""

import struct
import numpy as np
from typing import Dict, List, Tuple, Any


class IMUDataProcessor:
    """Декодування бінарних буферів IIO та векторне перетворення відліків у фізичні величини.

    Здійснює декодування цілочисельних відліків акселерометра та гіроскопа з бінарного
    буфера IIO, векторне перетворення у фізичні величини (м/с² та рад/с) за формулою
    масштабування IIO з урахуванням калібрувальних зсувів та підтримання масивів історії.
    """

    CHANNEL_ORDER = [
        "accel_x", "accel_y", "accel_z",
        "anglvel_x", "anglvel_y", "anglvel_z"
    ]

    def __init__(self, channels_metadata: Dict[str, Dict[str, Any]], history_size: int = 200) -> None:
        """Ініціалізація обробника даних IMU.

        :param channels_metadata: Метадані каналів (scale, offset, bytes_per_sample, endianness), отримані з IIOContextManager.
        :param history_size: Максимальна кількість кадрів у ковзному вікні історії.
        """
        self.channels_metadata = channels_metadata
        self.history_size = history_size

        # Розрахунок розміру одного кадру (в байтах)
        self.bytes_per_sample = sum(
            channels_metadata[ch]["bytes_per_sample"] for ch in self.CHANNEL_ORDER if ch in channels_metadata
        )

        # Створення впорядкованих векторів коефіцієнтів scale та offset для векторних обчислень NumPy
        self.scales = np.array(
            [channels_metadata[ch]["scale"] for ch in self.CHANNEL_ORDER if ch in channels_metadata],
            dtype=np.float64
        )
        self.offsets = np.array(
            [channels_metadata[ch]["offset"] for ch in self.CHANNEL_ORDER if ch in channels_metadata],
            dtype=np.float64
        )

        # Буфери історії для зберігання ковзного вікна вимірювань (6 каналів)
        # 0: accel_x, 1: accel_y, 2: accel_z, 3: gyro_x, 4: gyro_y, 5: gyro_z
        self.history = np.zeros((self.history_size, 6), dtype=np.float64)
        self.history_count: int = 0

    def decode_raw_buffer(self, raw_bytes: bytes) -> np.ndarray:
        """Декодує бінарні байтовий буфер IIO у масив цілих чисел NumPy.

        :param raw_bytes: Байтовий масив відліків з кільцевого буфера IIO.
        :return: Двовимірний масив цілих чисел NumPy форми (N_samples, 6).
        """
        if not raw_bytes or self.bytes_per_sample == 0:
            return np.empty((0, 6), dtype=np.int32)

        num_samples = len(raw_bytes) // self.bytes_per_sample
        if num_samples == 0:
            return np.empty((0, 6), dtype=np.int32)

        usable_bytes = num_samples * self.bytes_per_sample
        raw_int16 = np.frombuffer(raw_bytes[:usable_bytes], dtype=np.int16)

        try:
            raw_matrix = raw_int16.reshape((num_samples, len(self.CHANNEL_ORDER)))
        except ValueError:
            raw_matrix = self._decode_with_struct(raw_bytes[:usable_bytes], num_samples)

        return raw_matrix

    def _decode_with_struct(self, raw_bytes: bytes, num_samples: int) -> np.ndarray:
        """Резервне декодування бінарних кадрів через модуль struct."""
        fmt_str = "<" + "h" * len(self.CHANNEL_ORDER)
        sample_size = struct.calcsize(fmt_str)
        result = np.zeros((num_samples, len(self.CHANNEL_ORDER)), dtype=np.int32)

        for i in range(num_samples):
            offset = i * sample_size
            chunk = raw_bytes[offset:offset + sample_size]
            if len(chunk) == sample_size:
                result[i] = struct.unpack(fmt_str, chunk)

        return result

    def convert_to_physical(self, raw_matrix: np.ndarray) -> np.ndarray:
        """Векторне перетворення цілочисельних відліків у фізичні величини (м/с² та рад/с).

        Застосовує канонічну формулу підсистеми IIO ядра Linux:
        physical_value = (raw_value + offset) * scale

        :param raw_matrix: Масив сирих відліків (N_samples, 6).
        :return: Масив фізичних величин (N_samples, 6), де:
                 [0..2] - Акселерометр X, Y, Z (м/с²)
                 [3..5] - Гіроскоп X, Y, Z (рад/с)
        """
        if raw_matrix.size == 0:
            return np.empty((0, 6), dtype=np.float64)

        physical_matrix = (raw_matrix.astype(np.float64) + self.offsets) * self.scales
        return physical_matrix

    def update_history(self, physical_matrix: np.ndarray) -> None:
        """Оновлює ковзне вікно історії вимірів новими обробленими кадрами.

        :param physical_matrix: Масив фізичних величин (N_samples, 6).
        """
        num_new = physical_matrix.shape[0]
        if num_new == 0:
            return

        if num_new >= self.history_size:
            self.history = physical_matrix[-self.history_size:].copy()
            self.history_count = self.history_size
        else:
            self.history = np.roll(self.history, -num_new, axis=0)
            self.history[-num_new:] = physical_matrix
            self.history_count = min(self.history_size, self.history_count + num_new)

    def process_buffer(self, raw_bytes: bytes) -> np.ndarray:
        """Повний конвеєр обробки: декодування -> векторний розрахунок -> оновлення історії.

        :param raw_bytes: Сирий байтовий буфер від IIO.
        :return: Масив нових оброблених фізичних величин (N_samples, 6).
        """
        raw_matrix = self.decode_raw_buffer(raw_bytes)
        physical_matrix = self.convert_to_physical(raw_matrix)
        self.update_history(physical_matrix)
        return physical_matrix

    def get_history(self) -> Dict[str, np.ndarray]:
        """Повертає словник масивів історії вимірів для візуалізації.

        :return: Словник з масивами NumPy для осей акселерометра (accel_x, accel_y, accel_z)
                 та гіроскопа (gyro_x, gyro_y, gyro_z).
        """
        valid_history = self.history[-self.history_count:] if self.history_count < self.history_size else self.history

        return {
            "accel_x": valid_history[:, 0],
            "accel_y": valid_history[:, 1],
            "accel_z": valid_history[:, 2],
            "gyro_x": valid_history[:, 3],
            "gyro_y": valid_history[:, 4],
            "gyro_z": valid_history[:, 5]
        }
