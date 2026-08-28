from dataclasses import dataclass

# Усі затримки — у мілісекундах
@dataclass
class LatencyMs:
    sensor: float    # набір кадру сенсором
    encode: float    # стиснення кодеком (0 для аналогу)
    radio: float     # ефір + демодуляція
    decode: float    # розпакування (0 для аналогу)
    display: float   # вивід на екран окулярів

def glass_to_glass(p):
    return p.sensor + p.encode + p.radio + p.decode + p.display

# Скільки метрів апарат пролетить за час затримки
def blind_distance_m(latency_ms, speed_kmh):
    speed_ms = speed_kmh / 3.6                 # км/год → м/с
    return speed_ms * (latency_ms / 1000.0)    # мс → с

if __name__ == "__main__":
    o4 = LatencyMs(sensor=7, encode=12, radio=4, decode=6, display=8)
    total = glass_to_glass(o4)                 # 37.0 мс
    blind = blind_distance_m(total, 120.0)     # на 120 км/год

    print(f"Затримка: {total:.1f} мс")
    print(f"Наосліп:  {blind:.2f} м")
