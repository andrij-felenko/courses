"""
Модуль графічного візуалізатора результатів комп'ютерного зору (VisionOverlay).
Декодує відеокадри JPEG та накладає динамічні обмежувальні рамки (bounding boxes),
підписи класів, рівень впевненості детекції та інфо-блок затримок і FPS за допомогою OpenCV.
"""

from typing import Dict, List, Optional, Tuple
import cv2
import numpy as np


class VisionOverlay:
    """Клас для накладання динамічної графіки та системної телеметрії на відеокадри.
    
    Декодує стиснені зображення JPEG і графічно накладає колірно кодовані обмежувальні
    рамки (bounding boxes), текстові мітки об'єктів з оцінкою впевненості та інформаційний
    системний оверлей з показниками частоти кадрів (FPS) та затримок інференсу/передачі.
    """

    def __init__(
        self,
        class_names: Optional[Dict[int, str]] = None,
        conf_threshold: float = 0.35,
        font_scale: float = 0.5,
        font_thickness: int = 1,
    ) -> None:
        """Ініціалізація графічного візуалізатора.

        :param class_names: Словник відповідності ідентифікаторів класів їх назвам.
        :param conf_threshold: Поріг впевненості для відображення рамки детекції.
        :param font_scale: Масштаб шрифту OpenCV для підписів.
        :param font_thickness: Товщина ліній шрифту OpenCV.
        """
        self.class_names = class_names or {}
        self.conf_threshold = conf_threshold
        self.font_scale = font_scale
        self.font_thickness = font_thickness
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self._color_cache: Dict[int, Tuple[int, int, int]] = {}

    def _get_class_color(self, class_id: int) -> Tuple[int, int, int]:
        """Генерує унікальний та контрастний колір BGR для кожного class_id."""
        if class_id not in self._color_cache:
            hue = (class_id * 53) % 180
            hsv_color = np.uint8([[[hue, 225, 220]]])
            bgr_color = cv2.cvtColor(hsv_color, cv2.COLOR_HSV2BGR)[0][0]
            self._color_cache[class_id] = (int(bgr_color[0]), int(bgr_color[1]), int(bgr_color[2]))
        return self._color_cache[class_id]

    def decode_image(self, jpeg_bytes: bytes) -> np.ndarray:
        """Декодує байтовий масив JPEG у формат OpenCV BGR.

        :param jpeg_bytes: Байтовий масив стисненого зображення JPEG.
        :return: Двовимірний масив зображення NumPy (BGR).
        :raises ValueError: Якщо декодування зображення завершилося помилкою.
        """
        if not jpeg_bytes:
            raise ValueError("Отримано порожній масив байтів JPEG.")

        np_arr = np.frombuffer(jpeg_bytes, dtype=np.uint8)
        image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if image is None:
            raise ValueError("Не вдалося декодувати JPEG зображення (пошкоджені дані).")

        return image

    def draw_bounding_boxes(self, image: np.ndarray, detections: List[Dict]) -> np.ndarray:
        """Накладає обмежувальні рамки (bounding boxes) та підписи на зображення.

        :param image: Зображення OpenCV у форматі BGR.
        :param detections: Список словників із координатами та параметрами розпізнаних об'єктів.
        :return: Модифіковане зображення з накладеною графікою.
        """
        img_h, img_w = image.shape[:2]

        for det in detections:
            confidence = det.get("confidence", 0.0)
            if confidence < self.conf_threshold:
                continue

            class_id = det.get("class_id", 0)
            label = det.get("label") or self.class_names.get(class_id, f"Class {class_id}")
            bbox = det.get("bbox", [0, 0, 0, 0])

            if all(0.0 <= c <= 1.0 for c in bbox) and any(c > 0 for c in bbox):
                x_min = int(bbox[0] * img_w)
                y_min = int(bbox[1] * img_h)
                x_max = int(bbox[2] * img_w)
                y_max = int(bbox[3] * img_h)
            else:
                x_min, y_min, x_max, y_max = [int(c) for c in bbox]

            x_min = max(0, min(x_min, img_w - 1))
            y_min = max(0, min(y_min, img_h - 1))
            x_max = max(x_min + 1, min(x_max, img_w))
            y_max = max(y_min + 1, min(y_max, img_h))

            color = self._get_class_color(class_id)
            cv2.rectangle(image, (x_min, y_min), (x_max, y_max), color, 2)

            caption = f"{label} {confidence * 100:.1f}%"
            (text_w, text_h), baseline = cv2.getTextSize(caption, self.font, self.font_scale, self.font_thickness)

            label_bg_y1 = max(0, y_min - text_h - 6)
            label_bg_y2 = y_min
            cv2.rectangle(image, (x_min, label_bg_y1), (x_min + text_w + 6, label_bg_y2), color, cv2.FILLED)

            brightness = (color[0] * 11 + color[1] * 16 + color[2] * 5) / 32
            text_color = (0, 0, 0) if brightness > 128 else (255, 255, 255)

            cv2.putText(
                image,
                caption,
                (x_min + 3, label_bg_y2 - 3),
                self.font,
                self.font_scale,
                text_color,
                self.font_thickness,
                lineType=cv2.LINE_AA,
            )

        return image

    def draw_metrics_overlay(
        self,
        image: np.ndarray,
        fps: float,
        avg_fps: float,
        inference_ms: float,
        trans_ms: float,
        active_objects: int,
    ) -> np.ndarray:
        """Накладає напівпрозорий системний інфо-блок із метриками продуктивності.

        :param image: Кадр відеопотоку BGR.
        :param fps: Поточний миттєвий FPS.
        :param avg_fps: Середній FPS за часовий інтервал.
        :param inference_ms: Затримка нейромережевого інференсу на ESP32-S3 (мс).
        :param trans_ms: Затримка передачі даних по мережі/UART (мс).
        :param active_objects: Кількість виявлених об'єктів на кадрі.
        :return: Кадр із накладеним інформаційним оверлеєм.
        """
        overlay = image.copy()
        panel_w, panel_h = 320, 105

        cv2.rectangle(overlay, (10, 10), (10 + panel_w, 10 + panel_h), (20, 20, 20), cv2.FILLED)
        cv2.addWeighted(overlay, 0.7, image, 0.3, 0, image)

        cv2.rectangle(image, (10, 10), (10 + panel_w, 10 + panel_h), (0, 255, 200), 1)

        lines = [
            f"ESP32-S3 Edge AI Telemetry",
            f"FPS: {fps:.1f} (Avg: {avg_fps:.1f})",
            f"Inference Latency: {inference_ms:.1f} ms",
            f"Network/UART Latency: {trans_ms:.1f} ms",
            f"Active Detections: {active_objects}",
        ]

        y_pos = 28
        for i, line in enumerate(lines):
            color = (0, 255, 255) if i == 0 else (240, 240, 240)
            font_scale = 0.45 if i > 0 else 0.48
            thickness = 1 if i > 0 else 2
            cv2.putText(
                image,
                line,
                (18, y_pos),
                self.font,
                font_scale,
                color,
                thickness,
                lineType=cv2.LINE_AA,
            )
            y_pos += 18

        return image

    def process_frame(
        self,
        jpeg_bytes: bytes,
        metadata: Dict,
        metrics: Dict,
    ) -> np.ndarray:
        """Повний конвеєр обробки кадру: декодування, оверлей рамок та системних метрик."""
        image = self.decode_image(jpeg_bytes)
        detections = metadata.get("detections", [])
        image = self.draw_bounding_boxes(image, detections)

        active_objects = len([d for d in detections if d.get("confidence", 0) >= self.conf_threshold])
        image = self.draw_metrics_overlay(
            image=image,
            fps=metrics.get("instant_fps", 0.0),
            avg_fps=metrics.get("avg_fps", 0.0),
            inference_ms=metadata.get("inference_ms", 0.0),
            trans_ms=metrics.get("transmission_ms", 0.0),
            active_objects=active_objects,
        )

        return image
