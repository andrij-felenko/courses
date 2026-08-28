# -*- coding: utf-8 -*-
"""Розбір @PARAM/param.pck (ArduPilot): ім'я, тип, значення, заводське значення."""
import struct
from typing import NamedTuple, Optional

MAGIC_PLAIN, MAGIC_WITH_DEFAULTS = 0x671B, 0x671C
_FMT = {1: "<b", 2: "<h", 3: "<i", 4: "<f"}   # тип → формат значення
_SIZE = {1: 1, 2: 2, 3: 4, 4: 4}


class Param(NamedTuple):
    name: str
    type: int
    value: object
    fw_default: Optional[object]              # None ⇒ значення й є заводським


class PckError(ValueError):
    """Файл не є param.pck або обірваний — розбирати далі безглуздо."""


def parse(blob: bytes) -> list:
    if len(blob) < 6:
        raise PckError("файл коротший за заголовок")
    magic, num, total = struct.unpack_from("<HHH", blob, 0)
    if magic not in (MAGIC_PLAIN, MAGIC_WITH_DEFAULTS):
        raise PckError("чужий magic 0x%04X" % magic)
    if num > total:
        raise PckError("записів більше, ніж параметрів: %d > %d" % (num, total))

    out, i, last = [], 6, ""
    while len(out) < num:
        while i < len(blob) and blob[i] == 0:          # набивка
            i += 1
        if i + 2 > len(blob):
            raise PckError("файл урвався перед записом %d" % (len(out) + 1))

        b0, b1 = blob[i], blob[i + 1]
        i += 2
        ptype, has_default = b0 & 0x0F, bool(b0 >> 4 & 1)
        common, nlen = b1 & 0x0F, (b1 >> 4 & 0x0F) + 1

        if ptype not in _SIZE:
            raise PckError("невідомий тип %d" % ptype)
        if common + nlen > 16:
            raise PckError("ім'я довше за 16: %d + %d" % (common, nlen))
        if common > len(last):
            raise PckError("спільних %d байтів, а попереднє ім'я «%s»" % (common, last))

        size = _SIZE[ptype]
        need = nlen + size * (2 if has_default else 1)
        if i + need > len(blob):
            raise PckError("файл урвався всередині запису")

        name = last[:common] + blob[i:i + nlen].decode("ascii")
        i += nlen
        value = struct.unpack_from(_FMT[ptype], blob, i)[0]
        i += size
        default = None
        if has_default:
            default = struct.unpack_from(_FMT[ptype], blob, i)[0]
            i += size

        last = name                                    # база для наступного запису
        out.append(Param(name, ptype, value, default))

    if any(blob[i:]):                                  # хвіст — тільки набивка
        raise PckError("після останнього запису є не тільки набивка")
    return out


# ── застосування ────────────────────────────────────────────────────────────
# with open("param.pck", "rb") as f:
#     for p in parse(f.read()):
#         print(p.name, p.value, "(заводське", p.fw_default or p.value, ")")
