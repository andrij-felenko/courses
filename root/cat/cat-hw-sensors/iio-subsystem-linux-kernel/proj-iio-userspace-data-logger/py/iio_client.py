"""Модуль для підключення та взаємодії з підсистемою Industrial I/O (IIO) ядра Linux."""

import os
import sys
import time
import struct
import numpy as np
from typing import Dict, List, Optional, Tuple, Any

try:
    import iio
    HAS_LIBIIO = True
except ImportError:
    HAS_LIBIIO = False


class IIOClientError(Exception):
    """Кастомний виняток для обробки помилок клієнта підсистеми IIO Linux."""
    pass


class IIOContextManager:
    """Менеджер контексту та буфера IIO пристроїв (IMU) через бібліотеку libiio (pylibiio).

    Здійснює ініціалізацію контексту libiio, пошук інерційного пристрою IMU,
    зчитування параметрів scale та offset для активних каналів,
    а також створення та управління життєвим циклом кільцевого буфера IIO.
    """

    TARGET_CHANNELS = [
        "accel_x", "accel_y", "accel_z",
        "anglvel_x", "anglvel_y", "anglvel_z"
    ]

    def __init__(self, context_uri: str = "local:", device_name: Optional[str] = None) -> None:
        """Ініціалізація IIOContextManager.

        :param context_uri: URI контексту libiio (наприклад, 'local:', 'ip:192.168.1.50', 'xml:').
        :param device_name: Точна або часткова назва IMU-пристрою (наприклад, 'mpu6050', 'lsm6ds3').
        """
        self.context_uri = context_uri
        self.requested_device_name = device_name
        self.context: Optional[Any] = None
        self.device: Optional[Any] = None
        self.buffer: Optional[Any] = None
        self.channels_metadata: Dict[str, Dict[str, Any]] = {}
        self.enabled_channels: List[Any] = []
        self.is_simulated: bool = False
        self._sim_step: int = 0

    def connect(self) -> None:
        """Підключення до IIO-контексту ядра Linux та ідентифікація IMU-пристрою."""
        if not HAS_LIBIIO:
            print("[ІНФО] Модуль pylibiio (iio) не знайдено. Перехід у режим програмної симуляції IIO.")
            self.is_simulated = True
            self._init_simulation_metadata()
            return

        try:
            if self.context_uri == "local:":
                self.context = iio.Context()
            else:
                self.context = iio.Context(self.context_uri)
        except Exception as err:
            print(f"[УВАГА] Не вдалося створити IIO контекст ({err}). Перехід у режим симуляції.")
            self.is_simulated = True
            self._init_simulation_metadata()
            return

        self.device = self._find_imu_device(self.requested_device_name)
        if self.device is None:
            print("[УВАГА] IMU-пристрій не знайдено серед пристроїв IIO. Вмикаємо режим симуляції.")
            self.is_simulated = True
            self._init_simulation_metadata()
            return

        print(f"[УСПІХ] Знайдено IIO пристрій: {self.device.name} (id: {self.device.id})")
        self._read_channels_metadata()

    def _find_imu_device(self, preferred_name: Optional[str] = None) -> Optional[Any]:
        """Шукає інерційний модуль (IMU) у списку пристроїв IIO контексту."""
        if not self.context or not hasattr(self.context, "devices"):
            return None

        # 1. Пошук за точною чи частковою назвою
        if preferred_name:
            for dev in self.context.devices:
                if preferred_name.lower() in dev.name.lower() or preferred_name.lower() in dev.id.lower():
                    return dev

        # 2. Автоматичний пошук пристрою, який має акселерометр та гіроскоп
        for dev in self.context.devices:
            chan_ids = [ch.id for ch in dev.channels]
            has_accel = any("accel" in ch_id for ch_id in chan_ids)
            has_gyro = any("anglvel" in ch_id or "gyro" in ch_id for ch_id in chan_ids)
            if has_accel and has_gyro:
                return dev

        # 3. Резервний пошук будь-якого пристрою з акселерометром
        for dev in self.context.devices:
            chan_ids = [ch.id for ch in dev.channels]
            if any("accel" in ch_id for ch_id in chan_ids):
                return dev

        return None

    def _read_channels_metadata(self) -> None:
        """Зчитує метадані та атрибути масштабування (scale, offset, data_format) для активних каналів."""
        if not self.device:
            return

        self.channels_metadata.clear()
        self.enabled_channels.clear()

        # Вимикаємо всі канали спочатку для чистої конфігурації
        for chan in self.device.channels:
            chan.enabled = False

        for target_id in self.TARGET_CHANNELS:
            chan = self.device.find_channel(target_id)
            if not chan:
                # Спроба знайти канал за суфіксом або типом
                for ch in self.device.channels:
                    if target_id in ch.id or ch.id.endswith(target_id):
                        chan = ch
                        break

            if not chan:
                raise IIOClientError(f"Необхідний IIO-канал '{target_id}' не знайдено на пристрої {self.device.name}.")

            chan.enabled = True
            self.enabled_channels.append(chan)

            # Зчитування атрибута scale (масштабувальний коефіцієнт)
            scale_val = 1.0
            if "scale" in chan.attrs:
                try:
                    scale_val = float(chan.attrs["scale"].value)
                except ValueError:
                    scale_val = 1.0

            # Зчитування атрибута offset (калібрувальний зсув)
            offset_val = 0.0
            if "offset" in chan.attrs:
                try:
                    offset_val = float(chan.attrs["offset"].value)
                except ValueError:
                    offset_val = 0.0

            # Парсинг специфікацій бінарного формату (data_format)
            fmt = chan.data_format
            bits = fmt.bits if hasattr(fmt, "bits") else 16
            length = fmt.length // 8 if hasattr(fmt, "length") and fmt.length >= 8 else 2
            is_signed = fmt.is_signed if hasattr(fmt, "is_signed") else True
            is_be = fmt.is_be if hasattr(fmt, "is_be") else False
            scan_index = chan.scan_index if hasattr(chan, "scan_index") else len(self.channels_metadata)

            self.channels_metadata[target_id] = {
                "channel_obj": chan,
                "scale": scale_val,
                "offset": offset_val,
                "bits": bits,
                "bytes_per_sample": length,
                "is_signed": is_signed,
                "is_be": is_be,
                "scan_index": scan_index
            }

    def _init_simulation_metadata(self) -> None:
        """Ініціалізує метадані для режиму симуляції при відсутності обладнання."""
        scale_accel = 0.002392822  # (m/s^2) / LSB для діапазону ±8g MPU6050
        scale_gyro = 0.0010652644  # (rad/s) / LSB для діапазону ±2000dps MPU6050

        for idx, chan_id in enumerate(self.TARGET_CHANNELS):
            is_accel = "accel" in chan_id
            self.channels_metadata[chan_id] = {
                "channel_obj": None,
                "scale": scale_accel if is_accel else scale_gyro,
                "offset": 0.0,
                "bits": 16,
                "bytes_per_sample": 2,
                "is_signed": True,
                "is_be": False,
                "scan_index": idx
            }

    def create_buffer(self, samples_count: int = 100) -> None:
        """Створює кільцевий буфер IIO для потокового зчитування кадрів вимірювань.

        :param samples_count: Кількість відліків (кадрів) у кільцевому буфері.
        """
        if self.is_simulated:
            print(f"[СИМУЛЯЦІЯ] Створено віртуальний IIO буфер на {samples_count} кадрів.")
            return

        if not self.device:
            raise IIOClientError("Пристрій IIO не ініціалізовано. Спочатку викличте connect().")

        try:
            # Створення кільцевого буфера IIO (non-cyclic для безперервного зчитування)
            self.buffer = iio.Buffer(self.device, samples_count, cyclic=False)
            print(f"[УСПІХ] Кільцевий буфер IIO успішно створено ({samples_count} відліків).")
        except Exception as err:
            raise IIOClientError(f"Не вдалося створити кільцевий буфер IIO: {err}") from err

    def read_buffer_bytes(self, samples_count: int = 50) -> bytes:
        """Здійснює поповнення буфера та зчитування сирих бінарних даних.

        :param samples_count: Кількість кадрів для зчитування (використовується в режимі симуляції).
        :return: Байтовий масив зчитованих кадрів IIO.
        """
        if self.is_simulated:
            return self._generate_simulated_bytes(samples_count)

        if not self.buffer:
            raise IIOClientError("Буфер IIO не створено. Спочатку викличте create_buffer().")

        try:
            self.buffer.refill()
            return self.buffer.read()
        except Exception as err:
            raise IIOClientError(f"Помилка під час поповнення/зчитування буфера IIO: {err}") from err

    def _generate_simulated_bytes(self, samples_count: int) -> bytes:
        """Генерує реалістичні сирі бінарні дані IMU з гармонічними коливаннями та шумом."""
        raw_bytes = bytearray()
        t_base = self._sim_step * 0.02
        self._sim_step += samples_count

        for i in range(samples_count):
            t = t_base + i * 0.02
            # Акселерометр: Z близько +1g (9.81 m/s^2), X та Y коливаються
            ax_phys = 1.5 * np.sin(2 * np.pi * 0.5 * t) + np.random.normal(0, 0.1)
            ay_phys = 0.8 * np.cos(2 * np.pi * 0.3 * t) + np.random.normal(0, 0.1)
            az_phys = 9.81 + 0.5 * np.sin(2 * np.pi * 0.2 * t) + np.random.normal(0, 0.1)

            # Гіроскоп: кутові швидкості навколо осей (rad/s)
            gx_phys = 0.5 * np.cos(2 * np.pi * 1.0 * t) + np.random.normal(0, 0.02)
            gy_phys = 0.3 * np.sin(2 * np.pi * 0.8 * t) + np.random.normal(0, 0.02)
            gz_phys = 0.1 * np.cos(2 * np.pi * 0.4 * t) + np.random.normal(0, 0.02)

            phys_vals = [ax_phys, ay_phys, az_phys, gx_phys, gy_phys, gz_phys]

            # Перетворення у сирі цілочисельні значення (raw LSB)
            for idx, chan_id in enumerate(self.TARGET_CHANNELS):
                meta = self.channels_metadata[chan_id]
                scale = meta["scale"]
                offset = meta["offset"]
                val_phys = phys_vals[idx]
                raw_val = int(round(val_phys / scale - offset))
                # Обмеження діапазоном int16 [-32768, 32767]
                raw_val = max(-32768, min(32767, raw_val))
                raw_bytes.extend(struct.pack("<h", raw_val))

        return bytes(raw_bytes)

    def get_channel_metadata(self) -> Dict[str, Dict[str, Any]]:
        """Повертає метадані та коефіцієнти масштабування каналів."""
        return self.channels_metadata

    def destroy_buffer(self) -> None:
        """Безпечне вивільнення ресурсів буфера IIO."""
        if self.buffer is not None:
            try:
                del self.buffer
                self.buffer = None
                print("[ІНФО] Буфер IIO успішно знищено.")
            except Exception as err:
                print(f"[УВАГА] Помилка при вивільненні буфера IIO: {err}")

    def close(self) -> None:
        """Закриття IIO-контексту та деактивація каналів."""
        self.destroy_buffer()
        if self.device and hasattr(self.device, "channels"):
            for chan in self.device.channels:
                try:
                    chan.enabled = False
                except Exception:
                    pass
        self.context = None
        self.device = None
        print("[ЗАКІНЧЕННЯ] IIOContextManager успішно закрито.")

    def __enter__(self) -> "IIOContextManager":
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
