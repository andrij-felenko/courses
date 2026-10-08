"""
main.py
Головний виконуваний скрипт: ініціалізація зв'язку UART, запуск збору вимірювань,
керування конвеєром обчислення калібрувальної матриці в EllipsoidFitter
та передача підсумкових коефіцієнтів назад на мікроконтролер.
"""
import logging
import time
from typing import List

import numpy as np

from ellipsoid_fit import EllipsoidFitter, EllipsoidFitError
from serial_reader import SerialReader, SerialReaderError
from visualizer import CalibrationVisualizer

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def main() -> None:
    """Головний конвеєр автокалібрування цифрового компаса QMC5883L."""
    logging.info("=== Запуск системи автокалібрування QMC5883L через UART ===")

    port_name = "COM3"
    baud_rate = 115200
    target_samples = 350
    mock_mode = True
    output_image = "qmc5883l_calibration_3d.png"

    reader = SerialReader(
        port=port_name,
        baudrate=baud_rate,
        timeout=1.0,
        mock_mode=mock_mode,
    )

    fitter = EllipsoidFitter(target_field_strength=1.0)
    visualizer = CalibrationVisualizer(interactive=False)

    try:
        reader.connect()

        logging.info(f"Розпочато збір 3D-векторів магнітного поля (ціль: {target_samples} вибірок)...")
        logging.info("Повертайте пристрій QMC5883L в усіх напрямках (Roll, Pitch, Yaw)...")

        collected_raw: List[List[float]] = []

        while len(collected_raw) < target_samples:
            try:
                x, y, z = reader.read_sample()
                fitter.add_point(x, y, z)
                collected_raw.append([x, y, z])

                if len(collected_raw) % 50 == 0:
                    cov = fitter.evaluate_spatial_coverage()
                    logging.info(
                        f"Накопичено {len(collected_raw)}/{target_samples} вибірок | "
                        f"Покриття напрямків: {cov['coverage_pct']:.1f}% ({int(cov['octants_filled'])}/8 октантів)"
                    )
            except SerialReaderError as err:
                logging.warning(f"Пропущено пакет з UART: {err}")
                time.sleep(0.01)

        raw_array = np.array(collected_raw, dtype=np.float64)

        logging.info("Виконання алгебраїчної апроксимації еліпсоїда МНК...")
        hard_iron, soft_iron, rmse = fitter.fit(min_samples=100)

        calibrated_array = fitter.calibrate_batch(raw_array)

        logging.info("Передача підсумкових коефіцієнтів корекції на мікроконтролер...")
        reader.send_calibration(hard_iron, soft_iron)

        logging.info("Генерація 3D-графіка порівняння сирого еліпсоїда та відкаліброваної сфери...")
        visualizer.plot_comparison(
            raw_points=raw_array,
            calibrated_points=calibrated_array,
            hard_iron_offset=hard_iron,
            output_filepath=output_image,
        )

        logging.info("=== Процес калібрування QMC5883L успішно завершено ===")

    except (SerialReaderError, EllipsoidFitError) as e:
        logging.error(f"Помилка в ході калібрування: {e}")
    finally:
        reader.disconnect()
        visualizer.close()


if __name__ == "__main__":
    main()
