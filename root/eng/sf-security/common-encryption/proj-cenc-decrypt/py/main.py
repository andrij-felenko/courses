import struct

def parse_tenc(b):
    ver, off = b[0], 4          # FullBox: версія + прапорці
    off += 1                    # reserved
    if ver == 0:
        crypt = skip = 0
        off += 1
    else:
        crypt, skip = b[off] >> 4, b[off] & 0x0F
        off += 1
    is_protected, iv_size = b[off], b[off + 1]
    kid = b[off + 2:off + 18]
    off += 18
    const_iv = b''
    if is_protected and iv_size == 0:
        n = b[off]
        const_iv = b[off + 1:off + 1 + n]
    return dict(crypt=crypt, skip=skip, iv_size=iv_size, kid=kid, const_iv=const_iv)


def parse_senc(b, iv_size):
    has_subsamples = int.from_bytes(b[1:4], 'big') & 0x000002
    count, = struct.unpack_from('>I', b, 4)
    off, out = 8, []
    for _ in range(count):
        iv, off = b[off:off + iv_size], off + iv_size
        pairs = []
        if has_subsamples:
            m, = struct.unpack_from('>H', b, off)
            off += 2
            for _ in range(m):
                pairs.append(struct.unpack_from('>HI', b, off))   # 16 бітів і 32
                off += 6
        out.append((iv, pairs))
    return out
