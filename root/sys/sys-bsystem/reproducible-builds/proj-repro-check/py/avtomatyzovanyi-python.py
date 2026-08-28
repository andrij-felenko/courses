#!/usr/bin/env python3
"""Посекційний аналізатор двійкових розходжень файлів ELF."""
import sys
import hashlib
import struct

def parse_elf_sections(filepath):
    """Витягує назви, зміщення та розміри всіх секцій ELF."""
    with open(filepath, "rb") as f:
        data = f.read()

    # Перевірка магічного числа ELF (\x7fELF)
    if data[:4] != b"\x7fELF":
        raise ValueError(f"{filepath} не є файлом формату ELF")

    is_64bit = data[4] == 2
    endian = "<" if data[5] == 1 else ">"

    if is_64bit:
        e_shoff = struct.unpack_from(f"{endian}Q", data, 40)[0]
        e_shentsize = struct.unpack_from(f"{endian}H", data, 58)[0]
        e_shnum = struct.unpack_from(f"{endian}H", data, 60)[0]
        e_shstrndx = struct.unpack_from(f"{endian}H", data, 62)[0]
    else:
        e_shoff = struct.unpack_from(f"{endian}I", data, 32)[0]
        e_shentsize = struct.unpack_from(f"{endian}H", data, 46)[0]
        e_shnum = struct.unpack_from(f"{endian}H", data, 48)[0]
        e_shstrndx = struct.unpack_from(f"{endian}H", data, 50)[0]

    # Зчитування таблиці заголовків рядків назв секцій
    strtab_offset = e_shoff + e_shstrndx * e_shentsize
    if is_64bit:
        sh_offset = struct.unpack_from(f"{endian}Q", data, strtab_offset + 24)[0]
        sh_size = struct.unpack_from(f"{endian}Q", data, strtab_offset + 32)[0]
    else:
        sh_offset = struct.unpack_from(f"{endian}I", data, strtab_offset + 16)[0]
        sh_size = struct.unpack_from(f"{endian}I", data, strtab_offset + 20)[0]

    strtab = data[sh_offset : sh_offset + sh_size]

    sections = {}
    for i in range(e_shnum):
        entry_offset = e_shoff + i * e_shentsize
        if is_64bit:
            sh_name = struct.unpack_from(f"{endian}I", data, entry_offset)[0]
            sh_type = struct.unpack_from(f"{endian}I", data, entry_offset + 4)[0]
            sec_offset = struct.unpack_from(f"{endian}Q", data, entry_offset + 24)[0]
            sec_size = struct.unpack_from(f"{endian}Q", data, entry_offset + 32)[0]
        else:
            sh_name = struct.unpack_from(f"{endian}I", data, entry_offset)[0]
            sh_type = struct.unpack_from(f"{endian}I", data, entry_offset + 4)[0]
            sec_offset = struct.unpack_from(f"{endian}I", data, entry_offset + 16)[0]
            sec_size = struct.unpack_from(f"{endian}I", data, entry_offset + 20)[0]

        # SHT_NOBITS (наприклад, .bss) не має фізичного тіла у файлі
        if sh_type == 8 or sec_size == 0:
            continue

        name_end = strtab.find(b"\x00", sh_name)
        name = strtab[sh_name:name_end].decode("ascii", errors="replace")
        sec_bytes = data[sec_offset : sec_offset + sec_size]
        sec_hash = hashlib.sha256(sec_bytes).hexdigest()
        sections[name] = {"hash": sec_hash, "size": sec_size, "bytes": sec_bytes}

    return sections

def compare_binaries(file_a, file_b):
    sec_a = parse_elf_sections(file_a)
    sec_b = parse_elf_sections(file_b)

    all_names = sorted(set(sec_a.keys()) | set(sec_b.keys()))
    diff_found = False

    print(f"{'Секція':<25} | {'Розмір A':<10} | {'Розмір B':<10} | {'Статус':<15}")
    print("-" * 68)

    for name in all_names:
        if name not in sec_a:
            print(f"{name:<25} | {'-':<10} | {sec_b[name]['size']:<10} | ВІДСУТНЯ В A")
            diff_found = True
        elif name not in sec_b:
            print(f"{name:<25} | {sec_a[name]['size']:<10} | {'-':<10} | ВІДСУТНЯ В B")
            diff_found = True
        elif sec_a[name]["hash"] != sec_b[name]["hash"]:
            print(f"{name:<25} | {sec_a[name]['size']:<10} | {sec_b[name]['size']:<10} | РОЗБІЖНІСТЬ")
            diff_found = True
        else:
            print(f"{name:<25} | {sec_a[name]['size']:<10} | {sec_b[name]['size']:<10} | ІДЕНТИЧНО")

    return not diff_found

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Використання: {sys.argv[0]} <binary_A> <binary_B>")
        sys.exit(1)

    ok = compare_binaries(sys.argv[1], sys.argv[2])
    sys.exit(0 if ok else 1)
