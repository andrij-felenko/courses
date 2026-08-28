from dataclasses import dataclass

# Одна ланка конвеєра. Більшість ланок детерміновані (lo == hi);
# мінлива лише радіоланка двобічних систем, де hi > lo через пересилання.
@dataclass
class SpanMs:
    lo: float  # найкращий випадок, мс (у полі, без пересилань)
    hi: float  # найгірший випадок, мс (за бетоном, з пересиланнями)

# Повний конвеєр від скла до скла.
# sensor/encode/decode/display — обчислювальні (детерміновані тут);
# radio — єдина, що тримає діапазон.
@dataclass
class FpvSystem:
    name: str
    sensor: SpanMs    # набір кадру сенсором
    encode: SpanMs    # стиснення кодеком (lo=hi=0 для аналогу)
    radio: SpanMs     # ефір + (де)модуляція + можливі пересилання
    decode: SpanMs    # розпакування (lo=hi=0 для аналогу)
    display: SpanMs   # вивід на екран окулярів
    fps: int          # частота кадрів камери
