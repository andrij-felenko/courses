#!/usr/bin/env python3
"""sensedecode.py — те саме для рядка, скопійованого з журналу.
   ./sensedecode.py 'f0 00 03 00 00 20 03 0a 00 00 00 00 11 00 00 00 00 00'"""
import sys

KEYS = ["NO SENSE", "RECOVERED ERROR", "NOT READY", "MEDIUM ERROR",
        "HARDWARE ERROR", "ILLEGAL REQUEST", "UNIT ATTENTION", "DATA PROTECT",
        "BLANK CHECK", "VENDOR SPECIFIC", "COPY ABORTED", "ABORTED COMMAND",
        "(зарезервовано)", "VOLUME OVERFLOW", "MISCOMPARE", "COMPLETED"]


def normalize(b):
    """→ (код відповіді, ключ, ASC, ASCQ) або None, якщо сенс-даних немає."""
    if not b or (b[0] & 0x70) != 0x70:
        return None
    rc, n = b[0] & 0x7f, len(b)
    if rc < 0x72 and n > 7:
        n = min(n, b[7] + 8)              # пристрій сам сказав, скільки заповнив
    at = lambda i: b[i] if i < n else 0
    if rc >= 0x72:
        return rc, at(1) & 0xf, at(2), at(3)
    return rc, at(2) & 0xf, at(12), at(13)


def desc_find(b, want):
    """описувач заданого типу в ланцюгу розкладки 0x72/0x73."""
    if len(b) < 8 or not (0x72 <= (b[0] & 0x7f) <= 0x73) or b[7] == 0:
        return None
    end, i = 8 + min(b[7], len(b) - 8), 8
    while i + 2 <= end:
        step = b[i + 1] + 2
        if i + step > end:                # описувач обрізано — далі не читаємо
            break
        if b[i] == want:
            return b[i:i + step]
        i += step
    return None


def info_field(b):
    """номер збійного блока або None."""
    if (b[0] & 0x7f) in (0x70, 0x71):
        if len(b) < 7 or not (b[0] & 0x80):        # біт VALID знято
            return None
        return int.from_bytes(b[3:7], "big")       # чотири байти
    d = desc_find(b, 0x00)
    return int.from_bytes(d[4:12], "big") if d and d[1] == 0x0a else None


def check_sense(b):
    h = normalize(b)
    if h is None:
        return "FAILED"
    rc, key, asc, ascq = h
    if rc & 1:                                     # відкладена помилка
        return "NEEDS_RETRY"
    if key in (0x0, 0x1):
        return "SUCCESS"
    if key == 0xb:
        return "SUCCESS" if asc == 0x10 else "NEEDS_RETRY"
    if key in (0x2, 0x6):
        if (asc, ascq) in ((0x04, 0x01), (0x3f, 0x0e)):
            return "NEEDS_RETRY"
        return "FAILED" if (asc, ascq) == (0x04, 0x02) else "SUCCESS"
    if key == 0x3:
        return "SUCCESS" if asc in (0x11, 0x13, 0x14) else "NEEDS_RETRY"
    return "SUCCESS"


def decide(status, b):
    if status in (0x08, 0x28):
        return "ADD_TO_MLQUEUE"
    return check_sense(b) if status == 0x02 else "SUCCESS"


if __name__ == "__main__":
    args, status = sys.argv[1:], 0x02
    if len(args) >= 2 and args[0] == "-s":
        status, args = int(args[1], 16), args[2:]
    data = bytes(int(x, 16) for x in " ".join(args).replace(",", " ").split())
    h = normalize(data) if data else None
    if h:
        rc, key, asc, ascq = h
        kind = "описовий" if rc >= 0x72 else "фіксований"
        print("формат       : " + kind + (", ВІДКЛАДЕНА" if rc & 1 else ""))
        print(f"сенс-ключ    : {key:x}  {KEYS[key]}")
        print(f"ASC/ASCQ     : {asc:02x}/{ascq:02x}")
        blk = info_field(data)
        print(f"збійний блок : {blk if blk is not None else 'не вказано'}")
    else:
        print("сенс-дані    : немає або непридатні")
    print(f"вирок        : {decide(status, data)}")
