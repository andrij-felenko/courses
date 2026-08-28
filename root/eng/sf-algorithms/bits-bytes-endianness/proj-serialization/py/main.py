import struct


def put_u32_be(buf: bytearray, off: int, v: int) -> None:   # ціле — зсувами
    buf[off + 0] = (v >> 24) & 0xFF        # старший байт — першим (big-endian)
    buf[off + 1] = (v >> 16) & 0xFF
    buf[off + 2] = (v >>  8) & 0xFF
    buf[off + 3] = (v >>  0) & 0xFF


def get_u32_be(buf: bytes, off: int) -> int:                # дзеркально: збираємо назад
    return (buf[off + 0] << 24) | (buf[off + 1] << 16) \
         | (buf[off + 2] <<  8) |  buf[off + 3]


def put_f32_be(buf: bytearray, off: int, f: float) -> None:  # float — через байти, не зсувом
    # ">f" одразу пакує IEEE-754 у мережевому (big-endian) порядку —
    # struct сам вирівнює до дроту, розвертати вручну не треба:
    buf[off:off + 4] = struct.pack(">f", f)
