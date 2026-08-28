#!/usr/bin/env python3
"""Розшифрувати один сектор образу тим самим способом, що й ядро."""
import sys
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

SECTOR = 512


def xts_sector(key: bytes, sector: int, data: bytes) -> bytes:
    if len(key) not in (32, 64):
        raise SystemExit('XTS бере два ключі: разом 32 байти або 64')
    # plain64: номер сектора — 64-бітове число молодшим байтом уперед,
    # решта IV — нулі. Для 16-байтового IV це те саме, що 16 байтів
    # того самого числа в тому самому порядку.
    tweak = sector.to_bytes(16, 'little')
    dec = Cipher(algorithms.AES(key), modes.XTS(tweak)).decryptor()
    return dec.update(data) + dec.finalize()


def main(image, keyfile, hdr, sector):
    with open(keyfile, 'rb') as f:
        key = f.read()
    with open(image, 'rb') as f:
        f.seek((hdr + sector) * SECTOR)      # МІСЦЕ: зсув заголовка враховано
        ct = f.read(SECTOR)
    sys.stdout.buffer.write(xts_sector(key, sector, ct))   # ЗМІНА: без зсуву


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
