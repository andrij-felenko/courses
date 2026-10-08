"""Головний виконуваний скрипт для потокового збору та візуалізації даних IIO IMU."""

import sys
import time
from iio_client import IIOContextManager, IIOClientError
from data_processor import IMUDataProcessor
from visualizer import RealtimeVisualizer


def main() -> None:
    """Головна функція керування конвеєром збору, обробки та візуалізації даних IMU."""
    print("=" * 70)
    print(" КЛІЄНТ ЗБОРУ ДАНИХ ІНЕРЦІЙНОГО МОДУЛЯ (IMU) ЧЕРЕЗ LINUX IIO ")
    print("=" * 70)

    # Параметри системи
    history_size = 200        # Кількість кадрів у ковзному вікні візуалізації
    buffer_samples = 50       # Кількість відліків у кільцевому буфері IIO за один кадр
    update_interval_ms = 40   # Інтервал оновлення графіків (25 Гц)

    # 1. Ініціалізація контексту та підключення до IIO пристрою ядра Linux
    iio_client = IIOContextManager(context_uri="local:", device_name="mpu6050")

    try:
        print("[КРОК 1] Підключення до IIO-контексту та виявлення пристрою IMU...")
        iio_client.connect()

        metadata = iio_client.get_channel_metadata()
        print("\n[КРОК 2] Зчитані метадані каналів IIO:")
        for ch_id, info in metadata.items():
            print(f"  • Канал: {ch_id:<12} | Scale: {info['scale']:<12.9f} | Offset: {info['offset']:<6.1f} | Bits: {info['bits']}")

        # 2. Ініціалізація обробника даних NumPy
        print("\n[КРОК 3] Ініціалізація математичного процесора NumPy (IMUDataProcessor)...")
        processor = IMUDataProcessor(channels_metadata=metadata, history_size=history_size)

        # 3. Створення кільцевого буфера IIO
        print(f"\n[КРОК 4] Налаштування кільцевого буфера IIO ({buffer_samples} відліків)...")
        iio_client.create_buffer(samples_count=buffer_samples)

        # 4. Ініціалізація візуалізатора Matplotlib
        print("\n[КРОК 5] Запуск вікна динамічної візуалізації Matplotlib...")
        visualizer = RealtimeVisualizer(history_size=history_size, update_interval_ms=update_interval_ms)

        # Функція зворотного виклику для анімаційного циклу
        def frame_update_callback():
            try:
                # Зчитування бінарного блоку з буфера IIO
                raw_bytes = iio_client.read_buffer_bytes(samples_count=buffer_samples)
                # Векторне перетворення та оновлення ковзного вікна історії
                processor.process_buffer(raw_bytes)
            except IIOClientError as err:
                print(f"[ПОМИЛКА ЧИТАННЯ БУФЕРА] {err}")

            return processor.get_history()

        # 5. Запуск циклу візуалізації
        visualizer.start_animation(frame_update_callback)

    except IIOClientError as err:
        print(f"\n[КРИТИЧНА ПОМИЛКА IIO] {err}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n[ІНФО] Отримано сигнал зупинки користувачем (Ctrl+C).")
    except Exception as err:
        print(f"\n[НЕПЕРЕДБАЧЕНА ПОМИЛКА] {err}")
    finally:
        # 6. Безпечне вивільнення ресурсів
        print("\n[КРОК 6] Завершення роботи: очищення кільцевого буфера та закриття IIO контексту...")
        iio_client.close()
        print("[ГОТОВО] Всі ресурси успішно вивілено.")


if __name__ == "__main__":
    main()
