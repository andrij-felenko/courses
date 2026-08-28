import math
from dataclasses import dataclass

# Параметри пакета й радіо для розрахунку airtime.
@dataclass
class LoraCfg:
    sf: int              # коефіцієнт розширення, 7..12
    bw_hz: int           # ширина смуги в Гц (напр. 125000)
    payload: int         # довжина корисних даних, байтів
    cr: int              # кодова швидкість: 1..4  (1 = 4/5 ... 4 = 4/8)
    preamble: int = 8    # символів преамбули (типово 8)
    explicit_hdr: bool = True  # True = явний заголовок, False = неявний
    crc: bool = True     # True = додано CRC


# Час одного символа в наносекундах: Tsym = 2^SF / BW.
def symbol_time_ns(sf, bw_hz):
    return (1 << sf) * 1_000_000_000 // bw_hz


# Повний час пакета в ефірі (time on air) у мікросекундах.
def lora_airtime_us(c):
    tsym_ns = symbol_time_ns(c.sf, c.bw_hz)

    # DE (low data rate optimize) вмикається, коли символ довший за 16 мс.
    de = 1 if tsym_ns > 16_000_000 else 0     # 16 мс
    ih = 0 if c.explicit_hdr else 1           # implicit header
    crc = 1 if c.crc else 0

    # Число символів пакета за формулою Semtech.
    num = 8 * c.payload - 4 * c.sf + 28 + 16 * crc - 20 * ih
    den = 4 * (c.sf - 2 * de)
    groups = max(math.ceil(num / den) * (c.cr + 4), 0)
    payload_symb = 8 + groups

    # Преамбула: (n + 4.25) символів.
    t_preamble_ns = (c.preamble + 4.25) * tsym_ns
    t_payload_ns = payload_symb * tsym_ns

    return round((t_preamble_ns + t_payload_ns) / 1000)  # нс → мкс
