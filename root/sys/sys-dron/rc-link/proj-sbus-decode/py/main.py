from dataclasses import dataclass, field


@dataclass
class SbusData:
    ch: list[int] = field(default_factory=lambda: [0] * 16)  # 16 каналів, сирі значення 192..1792
    failsafe: bool = False   # приймач у failsafe — каналам не вірити
    frame_lost: bool = False  # цей кадр прийнято з помилкою


# Розпарсити 25-байтовий кадр SBUS. Повертає None, якщо рамка кадру не та.
def sbus_parse(frame: bytes) -> SbusData | None:
    if frame[0] != 0x0F or frame[24] != 0x00:
        return None                          # не наш кадр / зсув по байтах

    out = SbusData()
    bits = 0                                 # акумулятор бітів
    nbits = 0                                # скільки бітів у ньому зараз
    ch = 0                                   # який канал заповнюємо

    for i in range(1, 23):                   # байти даних 1..22
        if ch >= 16:
            break
        bits |= frame[i] << nbits            # досипати байт молодшими вперед
        nbits += 8
        while nbits >= 11 and ch < 16:       # назбиралося на канал?
            out.ch[ch] = bits & 0x07FF       # зняти молодші 11 бітів
            ch += 1
            bits >>= 11
            nbits -= 11

    out.frame_lost = bool(frame[23] & 0x04)  # біт 2 байта прапорців
    out.failsafe   = bool(frame[23] & 0x08)  # біт 3
    return out
