#!/usr/bin/env python3
"""Проставляє розмір і CRC32 образу в секцію .meta зібраного firmware.bin.

До компонування ні того, ні того не існує: компілятор кладе в структуру нулі,
а справжні значення відомі лише коли образ уже плаский. Крок навмисно окремий
і детермінований — жодного часу, жодного шляху, жодного випадкового поля:
той самий вхід дає той самий вихід байт у байт.

    python3 py/stamp_meta.py build/firmware.bin            # проштампувати
    python3 py/stamp_meta.py --verify build/firmware.bin   # звірити
    python3 py/stamp_meta.py --show build/firmware.bin     # прочитати метадані
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import os
import struct
import sys
import zlib
from typing import NamedTuple

# Розкладка мусить збігатися з fw_meta_t (c/include/build_meta.h)
# і fw::Meta (cpp/include/fw/build_meta.hpp).
LAYOUT = "<IHHIII40s32s"
META_SIZE = struct.calcsize(LAYOUT)
MAGIC = 0x544F4F4C  # 'TOOL'
VERSION = 1
SIZE_OFFSET = 12  # зсув поля image_size усередині структури
CRC_OFFSET = 16   # зсув поля image_crc32
ALIGNMENT = 4


class StampError(Exception):
    """Помилка, яку має бачити збірка, а не трасування Python."""


def find_meta(blob: bytes) -> int:
    """Зсув структури метаданих в образі.

    Шукаємо не за адресою з ELF, а за сигнатурою: так утиліта не залежить
    від розкладки й переживає зміну скрипта компонувальника. Знайдених
    збігів мусить бути рівно один — інакше ми не знаємо, який штампувати.
    """
    found = []
    for offset in range(0, len(blob) - META_SIZE + 1, ALIGNMENT):
        magic, version, size = struct.unpack_from("<IHH", blob, offset)
        if magic == MAGIC and version == VERSION and size == META_SIZE:
            found.append(offset)

    if not found:
        raise StampError(
            "секції .meta в образі немає: перевірте KEEP(*(.meta)) у linker.ld"
        )
    if len(found) > 1:
        places = ", ".join(hex(o) for o in found)
        raise StampError(f"знайдено кілька структур .meta ({places})")
    return found[0]


class Meta(NamedTuple):
    """Розібрана структура .meta — ті самі поля, що й fw_meta_t у прошивці."""

    offset: int
    magic: int
    version: int
    size: int
    build_epoch: int
    image_size: int
    image_crc32: int
    git_commit: str
    toolchain_id: str


def decode(blob: bytes, meta_offset: int) -> Meta:
    """Читає структуру з плаского образу за знайденим зсувом.

    Рівно те, що робить бутлоадер або сервісна утиліта: розкладка відома
    наперед, тож ані ELF, ані таблиці секцій розбирати не треба.
    """
    (magic, version, size, build_epoch, image_size, image_crc32,
     commit, toolchain) = struct.unpack_from(LAYOUT, blob, meta_offset)

    return Meta(
        offset=meta_offset,
        magic=magic,
        version=version,
        size=size,
        build_epoch=build_epoch,
        image_size=image_size,
        image_crc32=image_crc32,
        # git_commit — рівно 40 hex-символів без нульового байта,
        # toolchain_id коротший за поле й добитий нулями.
        git_commit=commit.decode("ascii", "replace"),
        toolchain_id=toolchain.split(b"\x00", 1)[0].decode("ascii", "replace"),
    )


def compute_crc(blob: bytes, meta_offset: int) -> int:
    """CRC32 усього образу з обнуленим полем image_crc32.

    Поле не можна враховувати в підрахунку: воно ж і є результатом.
    Прошивка при старті рахує рівно так само.
    """
    crc_at = meta_offset + CRC_OFFSET
    data = bytearray(blob)
    data[crc_at:crc_at + 4] = b"\x00\x00\x00\x00"
    return zlib.crc32(bytes(data)) & 0xFFFFFFFF


def stamp(path: str) -> None:
    with open(path, "rb") as handle:
        blob = handle.read()

    if not blob:
        raise StampError(f"{path}: порожній образ")

    meta_offset = find_meta(blob)
    data = bytearray(blob)

    # Розмір спершу: він входить у діапазон, над яким рахується CRC
    struct.pack_into("<I", data, meta_offset + SIZE_OFFSET, len(data))
    crc = compute_crc(bytes(data), meta_offset)
    struct.pack_into("<I", data, meta_offset + CRC_OFFSET, crc)

    # Запис через тимчасовий файл: обірваний штамп не лишить напівзаписаного
    # образу, який зовні виглядає зібраним.
    tmp_path = f"{path}.stamp"
    with open(tmp_path, "wb") as handle:
        handle.write(data)
    os.replace(tmp_path, path)

    digest = hashlib.sha256(data).hexdigest()
    print(f"stamp: зсув .meta 0x{meta_offset:04x}, розмір {len(data)} Б, CRC32 0x{crc:08x}")
    print(f"stamp: SHA-256 {digest}")


def verify(path: str) -> None:
    with open(path, "rb") as handle:
        blob = handle.read()

    meta = decode(blob, find_meta(blob))

    if meta.image_size == 0:
        raise StampError(f"{path}: образ не проштамповано")
    if meta.image_size != len(blob):
        raise StampError(
            f"{path}: у метаданих {meta.image_size} Б, а у файлі {len(blob)} Б"
        )

    actual = compute_crc(blob, meta.offset)
    if actual != meta.image_crc32:
        raise StampError(
            f"{path}: CRC32 не збігається — у метаданих 0x{meta.image_crc32:08x}, "
            f"порахували 0x{actual:08x}"
        )
    print(
        f"verify: {path} цілий, коміт {meta.git_commit[:12]}, "
        f"CRC32 0x{meta.image_crc32:08x}, {meta.image_size} Б"
    )


def show(path: str) -> None:
    """Виводить метадані образу так, як їх бачить бутлоадер із Flash.

    Саме цим і корисна секція .meta: щоб з'ясувати походження прошивки,
    достатньо плаского .bin — ні ELF, ні символів, ні тулчейну поруч.
    """
    with open(path, "rb") as handle:
        blob = handle.read()

    meta = decode(blob, find_meta(blob))
    when = datetime.datetime.fromtimestamp(meta.build_epoch, datetime.timezone.utc)

    print(f"файл        {path}")
    print(f"зсув .meta  0x{meta.offset:04x}, версія {meta.version}, {meta.size} Б")
    print(f"коміт       {meta.git_commit}")
    print(f"тулчейн     {meta.toolchain_id}")
    print(f"час збірки  {meta.build_epoch} ({when:%Y-%m-%d %H:%M:%S} UTC)")

    # Незаштампований образ — не помилка для цього режиму: саме так виглядає
    # свіжий результат objcopy, і побачити це буває потрібніше за виняток.
    if meta.image_size == 0:
        print("штамп       немає: stamp_meta.py по образу ще не проходив")
        return

    tail = "" if meta.image_size == len(blob) else f", а у файлі {len(blob)} Б"
    print(f"розмір      {meta.image_size} Б{tail}")
    print(f"CRC32       0x{meta.image_crc32:08x}")
    print(f"SHA-256     {hashlib.sha256(blob).hexdigest()}")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("image", help="плаский двійковий образ (firmware.bin)")
    # Режими взаємовиключні: штампування пише файл, решта — лише читає
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--verify",
        action="store_true",
        help="лише звірити вже вписані розмір і CRC32",
    )
    mode.add_argument(
        "--show",
        action="store_true",
        help="показати метадані образу, не змінюючи файла",
    )
    args = parser.parse_args(argv)

    try:
        if args.verify:
            verify(args.image)
        elif args.show:
            show(args.image)
        else:
            stamp(args.image)
    except FileNotFoundError:
        print(f"stamp_meta: немає файла {args.image}", file=sys.stderr)
        return 2
    except StampError as error:
        print(f"stamp_meta: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
