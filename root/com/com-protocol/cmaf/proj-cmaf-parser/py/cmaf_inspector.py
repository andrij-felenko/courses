#!/usr/bin/env python3
"""cmaf_inspector.py — утиліта швидкої інспекції боксів та валідації чанків CMAF."""
import sys
import struct

def parse_boxes(data, offset=0, depth=0):
    indent = "  " * depth
    while offset + 8 <= len(data):
        size32, fourcc = struct.unpack_from(">I4s", data, offset)
        fourcc_str = fourcc.decode("latin1", errors="replace")
        header_len = 8

        if size32 == 1:
            if offset + 16 > len(data):
                break
            size = struct.unpack_from(">Q", data, offset + 8)[0]
            header_len = 16
        elif size32 == 0:
            size = len(data) - offset
        else:
            size = size32

        if size < header_len or offset + size > len(data):
            print(f"{indent}❌ Помилка: невалідний розмір бокса {fourcc_str}: {size} байтів")
            break

        print(f"{indent}📦 [{fourcc_str}] розмір={size} байтів (зміщення=0x{offset:04X})")

        payload = data[offset + header_len:offset + size]

        # Рекурсивний розбір боксів-контейнерів
        if fourcc_str in ("moov", "moof", "trak", "mdia", "minf", "stbl", "mvex", "traf", "sinf", "schi"):
            parse_boxes(payload, offset=0, depth=depth + 1)
        elif fourcc_str == "tfdt" and len(payload) >= 4:
            ver = payload[0]
            if ver == 1 and len(payload) >= 12:
                dts = struct.unpack_from(">Q", payload, 4)[0]
                print(f"{indent}  ⏱ tfdt v1 baseMediaDecodeTime = {dts}")
            elif ver == 0 and len(payload) >= 8:
                dts = struct.unpack_from(">I", payload, 4)[0]
                print(f"{indent}  ⏱ tfdt v0 baseMediaDecodeTime = {dts}")
        elif fourcc_str == "mfhd" and len(payload) >= 8:
            seq = struct.unpack_from(">I", payload, 4)[0]
            print(f"{indent}  🔢 mfhd sequence_number = {seq}")

        offset += size

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Використання: python cmaf_inspector.py <сегмент.m4s | init.mp4>")
        sys.exit(1)

    with open(sys.argv[1], "rb") as f:
        content = f.read()

    print(f"Аналіз файлу: {sys.argv[1]} ({len(content)} байтів)")
    parse_boxes(content)
