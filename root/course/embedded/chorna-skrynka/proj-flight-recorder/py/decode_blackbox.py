#!/usr/bin/env python3
# decode_blackbox.py - Декодер двійкових знімків бортового реєстратора
import struct
import subprocess
import sys

SUBSYSTEMS = {
    0x00: "CORE",
    0x01: "POWER",
    0x02: "NAV",
    0x03: "ACTUATOR",
    0x04: "COMM"
}

EVENTS = {
    0x00: "NONE",
    0x01: "BOOT_OK",
    0x02: "FSM_TRANSITION",
    0x03: "BUS_NACK",
    0x04: "BUS_TIMEOUT",
    0x05: "VOLTAGE_WARN",
    0x06: "TEMP_CRITICAL",
    0xFE: "HARDFAULT",
    0xFF: "PANIC_ABORT"
}

def crc16_ccitt(data: bytes) -> int:
    crc = 0xFFFF
    for b in data:
        crc ^= (b << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return crc

def resolve_symbol(elf_path: str, address: int) -> str:
    if not elf_path:
        return f"0x{address:08X}"
    try:
        cmd = ["arm-none-eabi-addr2line", "-e", elf_path, "-f", "-C", f"0x{address:08X}"]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        lines = res.stdout.strip().split("\n")
        return f"{lines[0]} ({lines[1]})" if len(lines) >= 2 else f"0x{address:08X}"
    except Exception:
        return f"0x{address:08X}"

def parse_dump(dump_file: str, elf_file: str = ""):
    with open(dump_file, "rb") as f:
        raw = f.read()

    if len(raw) < 20:
        print("Помилка: файл занадто малий для тому реєстратора")
        return

    magic, boot_cnt, crash_cnt, head_idx, frozen = struct.unpack_from("<IIIII", raw, 0)
    if magic != 0x424F5831:
        print(f"Помилка: невідомий магічний заголовок 0x{magic:08X} (очікувався 'BOX1')")
        return

    print("=" * 75)
    print(f"ЗВІТ БОРТОВОГО РЕЄСТРАТОРА: Boots={boot_cnt}, Crashes={crash_cnt}, Head={head_idx}, Frozen={frozen}")
    print("=" * 75)

    offset = 20
    frame_size = 16
    total_frames = 256

    frames = []
    for i in range(total_frames):
        chunk = raw[offset + i * frame_size : offset + (i + 1) * frame_size]
        if len(chunk) < 16:
            break
        ts, sub, evt, fsm, p0, p1, p2, p3, p4, p5, crc = struct.unpack("<IBBH6BH", chunk)
        calc_crc = crc16_ccitt(chunk[:14])
        is_ok = (crc == calc_crc)
        payload = bytes([p0, p1, p2, p3, p4, p5])
        frames.append((i, ts, sub, evt, fsm, payload, is_ok))

    # Сортування кільцевого буфера у хронологічному порядку
    ordered_frames = frames[head_idx:] + frames[:head_idx]

    for slot, ts, sub, evt, fsm, payload, valid in ordered_frames:
        if ts == 0 and sub == 0 and evt == 0:
            continue # Порожній неініціалізований слот

        sub_name = SUBSYSTEMS.get(sub, f"0x{sub:02X}")
        evt_name = EVENTS.get(evt, f"0x{evt:02X}")
        status_str = "OK" if valid else "CRC_ERR"

        extra_info = ""
        if evt == 0xFE: # HardFault
            pc_addr = struct.unpack("<I", payload[:4])[0]
            fault_sym = resolve_symbol(elf_file, pc_addr)
            extra_info = f" | CRASH AT: {fault_sym}"
        else:
            extra_info = f" | Payload: {payload.hex()}"

        print(f"[{ts:8d} мс] [{sub_name:8s}] {evt_name:16s} (FSM=0x{fsm:04X}) [{status_str}]{extra_info}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Використання: python decode_blackbox.py <blackbox_dump.bin> [firmware.elf]")
        sys.exit(1)
    elf = sys.argv[2] if len(sys.argv) > 2 else ""
    parse_dump(sys.argv[1], elf)
