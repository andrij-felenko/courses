"""
Головний виконуваний модуль тестового інструментарію Edge AI для ESP32-S3.
Забезпечує конфігурацію параметрів зв'язку, координацію потокового прийому даних
через EdgeReceiver, передачу кадрів до VisionOverlay для візуалізації та підсумковий
аналіз метрик продуктивності у MetricsEvaluator.
"""

import argparse
import io
import json
import logging
import math
import random
import sys
import time
from typing import Tuple
import cv2
import numpy as np

from edge_receiver import EdgeReceiver, TelemetryParseError
from vision_overlay import VisionOverlay
from metrics_evaluator import MetricsEvaluator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("EdgeAI-Main")


class SyntheticStreamGenerator:
    """Симуляційний генератор потоку даних для тестування без фізичної плати ESP32-S3."""

    def __init__(self, width: int = 640, height: int = 480) -> None:
        self.width = width
        self.height = height
        self.frame_idx = 0

    def generate_frame(self) -> Tuple[bytes, dict]:
        """Генерує синтетичний JPEG кадр та метадані детекції."""
        self.frame_idx += 1
        img = np.zeros((self.height, self.width, 3), dtype=np.uint8)

        t = self.frame_idx * 0.05
        bg_color = (int(40 + 20 * math.sin(t)), int(30 + 10 * math.cos(t)), int(50 + 15 * math.sin(t * 0.5)))
        img[:] = bg_color

        x1 = int(100 + 80 * math.sin(t))
        y1 = int(120 + 50 * math.cos(t))
        x2 = x1 + 140
        y2 = y1 + 160
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 200, 255), -1)

        x3 = int(350 + 60 * math.cos(t * 0.7))
        y3 = int(200 + 40 * math.sin(t * 0.7))
        x4 = x3 + 120
        y4 = y3 + 120
        cv2.circle(img, ((x3 + x4) // 2, (y3 + y4) // 2), 60, (255, 100, 100), -1)

        _, jpeg_buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 80])
        jpeg_bytes = jpeg_buf.tobytes()

        now_ms = time.time() * 1000.0
        inference_ms = float(random.randint(28, 45))

        metadata = {
            "timestamp_ms": now_ms,
            "inference_ms": inference_ms,
            "send_timestamp_ms": now_ms - random.uniform(5.0, 12.0),
            "detections": [
                {
                    "class_id": 1,
                    "label": "person",
                    "confidence": float(round(random.uniform(0.82, 0.95), 2)),
                    "bbox": [x1 / self.width, y1 / self.height, x2 / self.width, y2 / self.height],
                },
                {
                    "class_id": 2,
                    "label": "sports_ball",
                    "confidence": float(round(random.uniform(0.75, 0.89), 2)),
                    "bbox": [x3 / self.width, y3 / self.height, x4 / self.width, y4 / self.height],
                },
            ],
        }

        return jpeg_bytes, metadata


def parse_arguments() -> argparse.Namespace:
    """Розбір аргументів командного рядка."""
    parser = argparse.ArgumentParser(
        description="Клієнтський інструментарій візуалізації та оцінки метрик Edge AI для ESP32-S3."
    )
    parser.add_argument(
        "--mode",
        choices=["wifi", "uart", "simulation"],
        default="simulation",
        help="Режим підключення: 'wifi', 'uart' або 'simulation' для автотестування (за замовчуванням: simulation).",
    )
    parser.add_argument("--host", default="192.168.1.100", help="IP-адреса ESP32-S3 у мережі Wi-Fi.")
    parser.add_argument("--port", type=int, default=8080, help="Мережевий порт HTTP сервака ESP32-S3.")
    parser.add_argument("--serial-port", default="COM3", help="Назва послідовного порту UART (наприклад, COM3 або /dev/ttyUSB0).")
    parser.add_argument("--baudrate", type=int, default=115200, help="Швидкість UART (за замовчуванням: 115200).")
    parser.add_argument("--conf-threshold", type=float, default=0.4, help="Поріг впевненості для відображення рамок (0.0-1.0).")
    parser.add_argument("--no-display", action="store_true", help="Вимкнути відображення графічного вікна OpenCV.")
    parser.add_argument("--max-frames", type=int, default=0, help="Максимальна кількість кадрів для обробки (0 - без обмежень).")
    return parser.parse_args()


def main() -> None:
    """Головний функціональний конвеєр додатка."""
    args = parse_arguments()

    logger.info(f"Запуск клієнта верифікації ESP32-S3 Edge AI у режимі '{args.mode}'")

    receiver = None
    synth_gen = None

    if args.mode == "simulation":
        synth_gen = SyntheticStreamGenerator()
    else:
        receiver = EdgeReceiver(
            mode=args.mode,
            host=args.host,
            port=args.port,
            serial_port=args.serial_port,
            baudrate=args.baudrate,
        )
        try:
            receiver.connect()
        except TelemetryParseError as err:
            logger.error(f"Не вдалося встановити початкове з'єднання: {err}")
            sys.exit(1)

    overlay = VisionOverlay(conf_threshold=args.conf_threshold)
    evaluator = MetricsEvaluator(window_size=100)

    window_name = "ESP32-S3 Edge AI Vision Overlay & Metrics"
    if not args.no_display:
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 800, 600)

    processed_frames = 0

    try:
        while True:
            if args.max_frames > 0 and processed_frames >= args.max_frames:
                logger.info(f"Досягнуто ліміт обробки у {args.max_frames} кадрів. Завершення...")
                break

            try:
                if args.mode == "simulation":
                    jpeg_bytes, metadata = synth_gen.generate_frame()
                    time.sleep(0.033)
                else:
                    jpeg_bytes, metadata = receiver.read_frame()
            except TelemetryParseError as err:
                logger.warning(f"Помилка парсингу телеметрії: {err}. Пропуск кадру...")
                time.sleep(0.05)
                continue

            metrics_data = evaluator.update(
                inference_ms=metadata.get("inference_ms", 0.0),
                send_timestamp_ms=metadata.get("send_timestamp_ms"),
                receive_timestamp_ms=metadata.get("receive_timestamp_ms"),
                detections=metadata.get("detections"),
            )

            rendered_frame = overlay.process_frame(jpeg_bytes, metadata, metrics_data)
            processed_frames += 1

            if not args.no_display:
                cv2.imshow(window_name, rendered_frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q") or key == 27:
                    logger.info("Отримано команду виходу від користувача.")
                    break

    except KeyboardInterrupt:
        logger.info("Переривання користувачем (Ctrl+C).")
    finally:
        if receiver:
            receiver.disconnect()
        if not args.no_display:
            cv2.destroyAllWindows()

        evaluator.print_report()


if __name__ == "__main__":
    main()
