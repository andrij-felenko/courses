import struct

IPPROTO_TCP, IPPROTO_UDP = 6, 17


def sum_words(data: bytes, start: int = 0) -> int:
    """Долити шматок у біжучу (незгорнуту) суму."""
    if len(data) % 2:
        data += b"\x00"          # нуль СПРАВА — лише для останнього шматка
    return start + sum(struct.unpack("!%dH" % (len(data) // 2), data))


def fold(s: int) -> int:
    """Загорнути перенос: двох згортань досить для будь-якого 32-бітного s."""
    s = (s & 0xFFFF) + (s >> 16)
    s = (s & 0xFFFF) + (s >> 16)
    return s & 0xFFFF
