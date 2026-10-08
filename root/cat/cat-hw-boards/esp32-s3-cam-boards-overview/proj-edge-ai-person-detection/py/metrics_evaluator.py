"""
Модуль для оцінки та аналізу метрик продуктивності Edge AI пристроїв (MetricsEvaluator).
Обчислює затримки інференсу (latency), передачі даних, розраховує частоту кадрів (FPS),
статистичні показники (середнє, медіана, відхилення) та оцінює якість детекції.
"""

from collections import deque
import math
import time
from typing import Dict, List, Optional
import numpy as np


class MetricsEvaluator:
    """Клас для накопичення часових міток, вимірювання затримок та оцінки продуктивності.
    
    Здійснює моніторинг частоти кадрів (FPS), оцінку часових затримок нейромережевого
    інференсу на ESP32-S3 та затримок передачі по мережі/UART. Акумулює статистику
    для формування підсумкового звіту продуктивності.
    """

    def __init__(self, window_size: int = 100) -> None:
        """Ініціалізація аналізатора метрик.

        :param window_size: Розмір ковзного вікна для обчислення локальних середніх значений.
        """
        self.window_size = window_size
        self._inference_latencies = deque(maxlen=window_size)
        self._transmission_latencies = deque(maxlen=window_size)
        self._total_latencies = deque(maxlen=window_size)
        self._frame_times = deque(maxlen=window_size)
        self._confidence_scores = deque(maxlen=1000)

        self._start_time: float = time.time()
        self._last_frame_time: Optional[float] = None
        self._total_frames_count: int = 0
        self._total_detections_count: int = 0

    def update(
        self,
        inference_ms: float,
        send_timestamp_ms: Optional[float] = None,
        receive_timestamp_ms: Optional[float] = None,
        detections: Optional[List[Dict]] = None,
    ) -> Dict[str, float]:
        """Оновлює статистичні дані на основі параметрів нового кадру.

        :param inference_ms: Затримка виконання нейромережевої моделі на ESP32-S3 (мс).
        :param send_timestamp_ms: Часова мітка відправки кадру з ESP32-S3 (мс).
        :param receive_timestamp_ms: Часова мітка прийому кадру на ПК (мс).
        :param detections: Список розпізнаних об'єктів для аналізу точності.
        :return: Словник з поточними миттєвими метриками.
        """
        now = time.time()
        self._total_frames_count += 1

        if self._last_frame_time is not None:
            delta_t = now - self._last_frame_time
            if delta_t > 0:
                instant_fps = 1.0 / delta_t
                self._frame_times.append(delta_t)
            else:
                instant_fps = 0.0
        else:
            instant_fps = 0.0
        self._last_frame_time = now

        if send_timestamp_ms and receive_timestamp_ms and receive_timestamp_ms >= send_timestamp_ms:
            trans_ms = receive_timestamp_ms - send_timestamp_ms
        else:
            trans_ms = 0.0

        total_latency_ms = inference_ms + trans_ms

        self._inference_latencies.append(inference_ms)
        self._transmission_latencies.append(trans_ms)
        self._total_latencies.append(total_latency_ms)

        if detections:
            self._total_detections_count += len(detections)
            for d in detections:
                if "confidence" in d:
                    self._confidence_scores.append(d["confidence"])

        avg_fps = (1.0 / np.mean(self._frame_times)) if self._frame_times else instant_fps

        return {
            "instant_fps": instant_fps,
            "avg_fps": float(avg_fps),
            "inference_ms": inference_ms,
            "transmission_ms": trans_ms,
            "total_latency_ms": total_latency_ms,
        }

    def get_summary(self) -> Dict:
        """Обчислює зведені статистичні показники продуктивності системи.

        :return: Словник з повним набором підсумкових метрик.
        """
        elapsed_time = time.time() - self._start_time
        overall_avg_fps = self._total_frames_count / elapsed_time if elapsed_time > 0 else 0.0

        def calc_stats(data: deque) -> Dict[str, float]:
            if not data:
                return {"mean": 0.0, "median": 0.0, "std": 0.0, "min": 0.0, "max": 0.0, "p95": 0.0}
            arr = np.array(data)
            return {
                "mean": float(np.mean(arr)),
                "median": float(np.median(arr)),
                "std": float(np.std(arr)),
                "min": float(np.min(arr)),
                "max": float(np.max(arr)),
                "p95": float(np.percentile(arr, 95)),
            }

        avg_conf = float(np.mean(self._confidence_scores)) if self._confidence_scores else 0.0

        return {
            "total_frames": self._total_frames_count,
            "elapsed_seconds": elapsed_time,
            "overall_fps": overall_avg_fps,
            "inference_stats_ms": calc_stats(self._inference_latencies),
            "transmission_stats_ms": calc_stats(self._transmission_latencies),
            "total_latency_stats_ms": calc_stats(self._total_latencies),
            "total_detections": self._total_detections_count,
            "avg_detections_per_frame": self._total_detections_count / max(1, self._total_frames_count),
            "mean_confidence": avg_conf,
        }

    def print_report(self) -> None:
        """Виводить у консоль відформатований текстовий звіт із метриками продуктивності."""
        s = self.get_summary()
        inf = s["inference_stats_ms"]
        tx = s["transmission_stats_ms"]
        tot = s["total_latency_stats_ms"]

        report = f"""
======================================================================
               ЗВІТ ПРОДУКТИВНОСТІ EDGE AI (ESP32-S3)
======================================================================
Загальний час тестування:    {s['elapsed_seconds']:.2f} сек.
Оброблено відеокадрів:        {s['total_frames']}
Середня частота кадрів (FPS): {s['overall_fps']:.2f}
Всього виявлено об'єктів:    {s['total_detections']} (сер. {s['avg_detections_per_frame']:.2f} на кадр)
Середня впевненість моделі:   {s['mean_confidence'] * 100:.1f}%

--- Затримка інференсу нейромережі (Inference Latency, ms) ---
  Середнє:  {inf['mean']:.2f} мс  | Медіана: {inf['median']:.2f} мс
  Мін / Макс: {inf['min']:.2f} / {inf['max']:.2f} мс | 95-й перцентиль: {inf['p95']:.2f} мс
  Стандартне відхилення: {inf['std']:.2f} мс

--- Затримка передачі даних (Network / UART Latency, ms) ---
  Середнє:  {tx['mean']:.2f} мс  | Медіана: {tx['median']:.2f} мс
  Мін / Макс: {tx['min']:.2f} / {tx['max']:.2f} мс | 95-й перцентиль: {tx['p95']:.2f} мс

--- Загальна затримка конвеєра (End-to-End Latency, ms) ---
  Середнє:  {tot['mean']:.2f} мс  | Медіана: {tot['median']:.2f} мс
  95-й перцентиль: {tot['p95']:.2f} мс
======================================================================
"""
        print(report)

    def reset(self) -> None:
        """Скидає всі накопичені статистичні лічильники та масиви."""
        self._inference_latencies.clear()
        self._transmission_latencies.clear()
        self._total_latencies.clear()
        self._frame_times.clear()
        self._confidence_scores.clear()
        self._start_time = time.time()
        self._last_frame_time = None
        self._total_frames_count = 0
        self._total_detections_count = 0
