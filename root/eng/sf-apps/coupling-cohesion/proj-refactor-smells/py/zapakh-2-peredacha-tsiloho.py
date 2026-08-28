@dataclass
class Reading:
    celsius: float
    raw: int
    timestamp: int
    sensor_id: int
    crc: int
    rssi: int           # сила сигналу, якщо давач бездротовий
    # …структура росте, її чіпають з десятка причин

# Зчеплення за зліпком: бере всю структуру, використовує ДВА поля
def apply_calibration(r: Reading, tbl: CalTable) -> float:
    offset = tbl.lookup(r.sensor_id)         # потрібне поле 1
    return r.celsius + offset                # потрібне поле 2
    # решта Reading тут не використана — але функція від неї залежить
