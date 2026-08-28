def _enc4(d):
    b3, b5, b6, b7 = (d >> 3) & 1, (d >> 2) & 1, (d >> 1) & 1, d & 1
    b1, b2, b4 = b3 ^ b5 ^ b7, b3 ^ b6 ^ b7, b5 ^ b6 ^ b7
    return b1 | (b2 << 1) | (b3 << 2) | (b4 << 3) | (b5 << 4) | (b6 << 5) | (b7 << 6)

def _bit(w, i):
    return (w >> (i - 1)) & 1

def _dec7(w):
    s = ((_bit(w, 1) ^ _bit(w, 3) ^ _bit(w, 5) ^ _bit(w, 7))
         | ((_bit(w, 2) ^ _bit(w, 3) ^ _bit(w, 6) ^ _bit(w, 7)) << 1)
         | ((_bit(w, 4) ^ _bit(w, 5) ^ _bit(w, 6) ^ _bit(w, 7)) << 2))
    if s:
        w ^= 1 << (s - 1)         # синдром — це просто НОМЕР зіпсутого біта
    return (_bit(w, 3) << 3) | (_bit(w, 5) << 2) | (_bit(w, 6) << 1) | _bit(w, 7)

HAM_ENC = [_enc4(d) for d in range(16)]     # 16 слів по 7 бітів
HAM_DEC = [_dec7(w) for w in range(128)]    # будь-які 7 бітів → півбайт

def inner_encode(stream):
    bits = []
    for byte in stream:
        for nib in (byte >> 4, byte & 15):
            w = HAM_ENC[nib]
            bits.extend((w >> i) & 1 for i in range(7))
    return bits                              # 14 бітів на байт

def inner_decode(bits):
    out = []
    for i in range(0, len(bits), 14):
        hi = HAM_DEC[sum(bits[i + k] << k for k in range(7))]
        lo = HAM_DEC[sum(bits[i + 7 + k] << k for k in range(7))]
        out.append((hi << 4) | lo)
    return out
