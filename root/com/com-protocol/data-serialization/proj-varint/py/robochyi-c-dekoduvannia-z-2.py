# Той самий алгоритм; межа зсуву тепер 64.
def varint_decode_u64(buf: bytes):
    result = 0
    shift = 0
    for i, b in enumerate(buf):
        result |= (b & 0x7F) << shift
        if (b & 0x80) == 0:
            return result & 0xFFFFFFFFFFFFFFFF, i + 1
        shift += 7
        if shift >= 64:
            return None, 0
    return None, 0
