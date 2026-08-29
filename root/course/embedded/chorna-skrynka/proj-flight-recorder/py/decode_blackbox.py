#!/usr/bin/env python3
"""Декодер двійкових знімків бортового реєстратора.

Читає файл, знятий програматором зі слота FRAM або з дампа .noinit, розкручує
кільцевий буфер у хронологічний порядок, перевіряє CRC кожного кадру й
перетворює адреси Program Counter на назви функцій через arm-none-eabi-addr2line.
Розкладка структур мусить збігатися з c/flight_recorder_core.h.
"""

import argparse
import struct
import subprocess
import sys

MAGIC = 0x424F5831  # 'BOX1'
HEADER_FORMAT = "<IIIIIIHH"  # magic, boot, crash, capacity, sequence, frozen, crc, reserved
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)  # 28
HEADER_CRC_LEN = 16  # CRC покриває лише незмінну частину: magic, boot, crash, capacity
FRAME_FORMAT = "<IBBH6sH"
FRAME_SIZE = struct.calcsize(FRAME_FORMAT)  # 16

SUBSYSTEMS = {
    0x00: "CORE",
    0x01: "POWER",
    0x02: "NAV",
    0x03: "ACTUATOR",
    0x04: "COMM",
}

EVENTS = {
    0x00: "NONE",
    0x01: "BOOT_OK",
    0x02: "FSM_TRANSITION",
    0x03: "BUS_NACK",
    0x04: "BUS_TIMEOUT",
    0x05: "VOLTAGE_WARN",
    0x06: "TEMP_CRITICAL",
    0xFC: "FAULT_CONTEXT",
    0xFD: "FAULT_ADDR",
    0xFE: "HARDFAULT",
    0xFF: "PANIC_ABORT",
}

EVT_FAULT_CONTEXT = 0xFC
EVT_FAULT_ADDR = 0xFD
EVT_HARDFAULT = 0xFE
EVT_PANIC_ABORT = 0xFF

# Біти CFSR: MMFSR (0..7), BFSR (8..15), UFSR (16..31)
CFSR_BITS = [
    (0, "IACCVIOL", "вибірка інструкції з забороненої області"),
    (1, "DACCVIOL", "доступ до даних, заблокований MPU"),
    (3, "MUNSTKERR", "збій розстекування при поверненні з винятку"),
    (4, "MSTKERR", "збій стекування на вході у виняток (переповнення стека)"),
    (5, "MLSPERR", "збій відкладеного збереження регістрів FPU"),
    (8, "IBUSERR", "помилка шини при вибірці інструкції"),
    (9, "PRECISERR", "точна помилка шини, адреса у BFAR"),
    (10, "IMPRECISERR", "неточна помилка шини (запис через буфер)"),
    (11, "UNSTKERR", "помилка шини при розстекуванні"),
    (12, "STKERR", "помилка шини при стекуванні"),
    (13, "LSPERR", "помилка шини при збереженні контексту FPU"),
    (16, "UNDEFINSTR", "невідомий код інструкції"),
    (17, "INVSTATE", "спроба виконати код не в наборі Thumb"),
    (18, "INVPC", "неприпустиме значення EXC_RETURN або PC"),
    (19, "NOCP", "звернення до відсутнього співпроцесора (вимкнений FPU)"),
    (24, "UNALIGNED", "непарний доступ при піднятому UNALIGN_TRP"),
    (25, "DIVBYZERO", "ділення на нуль при піднятому DIV_0_TRP"),
]

HFSR_FLAGS = [
    (0x01, "VECTTBL", "збій читання таблиці векторів"),
    (0x02, "FORCED", "налаштований виняток ескалювали в HardFault"),
    (0x04, "DEBUGEVT", "подія відлагоджувача"),
]


def crc16_ccitt(data: bytes) -> int:
    crc = 0xFFFF
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return crc


class SymbolResolver:
    """Обгортка над addr2line. Тримає кеш: у дампі та сама адреса трапляється
    десятками разів, а кожен запуск процесу коштує дорожче за весь розбір."""

    def __init__(self, elf_path: str, toolchain: str):
        self.elf_path = elf_path
        self.tool = toolchain + "addr2line"
        self.cache: dict[int, str] = {}
        self.available = bool(elf_path)

    def resolve(self, address: int) -> str:
        plain = f"0x{address:08X}"
        if not self.available or address == 0:
            return plain
        if address in self.cache:
            return self.cache[address]

        # Молодший біт адреси на Cortex-M позначає набір Thumb, у таблиці
        # символів його немає — інакше addr2line не знаходить нічого.
        query = address & ~1
        try:
            result = subprocess.run(
                [self.tool, "-e", self.elf_path, "-f", "-C", f"0x{query:08X}"],
                capture_output=True,
                text=True,
                check=True,
            )
        except FileNotFoundError:
            print(f"[!] {self.tool} не знайдено — адреси лишаються числами", file=sys.stderr)
            self.available = False
            return plain
        except subprocess.CalledProcessError:
            self.cache[address] = plain
            return plain

        lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        if len(lines) >= 2 and lines[0] != "??":
            answer = f"{lines[0]} ({lines[1]})"
        else:
            answer = plain
        self.cache[address] = answer
        return answer


class Frame:
    def __init__(self, slot: int, raw: bytes):
        self.slot = slot
        self.raw = raw
        (self.timestamp, self.subsystem, self.event, self.fsm,
         self.payload, self.crc) = struct.unpack(FRAME_FORMAT, raw)
        self.crc_ok = self.crc == crc16_ccitt(raw[:14])

    @property
    def empty(self) -> bool:
        return self.raw == bytes(FRAME_SIZE)

    def payload_u32(self) -> int:
        return struct.unpack("<I", self.payload[:4])[0]

    def payload_u16(self) -> int:
        return struct.unpack("<H", self.payload[4:6])[0]


def parse_header(raw: bytes) -> dict | None:
    if len(raw) < HEADER_SIZE:
        return None
    magic, boots, crashes, capacity, sequence, frozen, crc, _ = struct.unpack_from(
        HEADER_FORMAT, raw, 0
    )
    if magic != MAGIC:
        return None
    return {
        "boots": boots,
        "crashes": crashes,
        "capacity": capacity,
        "sequence": sequence,
        "frozen": frozen,
        "crc_ok": crc == crc16_ccitt(raw[:HEADER_CRC_LEN]),
    }


def describe_fault(frame: Frame, resolver: SymbolResolver) -> list[str]:
    """Три кадри аварії разом дають повну картину збою."""
    lines = []
    if frame.event == EVT_HARDFAULT:
        pc = frame.payload_u32()
        cfsr = (frame.fsm << 16) | frame.payload_u16()
        lines.append(f"    впало на: {resolver.resolve(pc)}")
        lines.append(f"    CFSR = 0x{cfsr:08X}")
        for bit, name, meaning in CFSR_BITS:
            if cfsr & (1 << bit):
                lines.append(f"      · {name}: {meaning}")
    elif frame.event == EVT_FAULT_ADDR:
        address = frame.payload_u32()
        valid = frame.payload_u16()
        source = {1: "MMFAR", 2: "BFAR"}.get(valid, "")
        if source:
            lines.append(f"    адреса збою ({source}) = 0x{address:08X}")
        else:
            lines.append("    адреса збою невідома: біт дійсності не стояв")
        for mask, name, meaning in HFSR_FLAGS:
            if frame.fsm & mask:
                lines.append(f"      · HFSR.{name}: {meaning}")
    elif frame.event == EVT_FAULT_CONTEXT:
        lr = frame.payload_u32()
        ipsr = frame.payload_u16()
        exc_return = frame.fsm
        stack = "PSP (стек потоку)" if exc_return & 0x04 else "MSP (стек ядра)"
        origin = f"виняток №{ipsr}" if ipsr else "потік застосунку"
        lines.append(f"    повернення в: {resolver.resolve(lr)}")
        lines.append(f"    кадр лежав на {stack}; аварію спіймано з: {origin}")
        if not exc_return & 0x10:
            lines.append("      · у кадрі є регістри FPU (розширений стековий кадр)")
    elif frame.event == EVT_PANIC_ABORT:
        lines.append(f"    програмна паніка, контекст = 0x{frame.payload_u32():08X}")
    return lines


def decode(path: str, elf: str, toolchain: str, show_empty: bool) -> int:
    with open(path, "rb") as handle:
        raw = handle.read()

    header = parse_header(raw)
    resolver = SymbolResolver(elf, toolchain)

    if header is None:
        # Файл без заголовка — програматор часто знімає тільки область кадрів.
        print("[i] Заголовок не розпізнано: читаю файл як суцільний масив кадрів")
        frames_raw = raw
        capacity = len(raw) // FRAME_SIZE
        head = 0
    else:
        capacity = header["capacity"]
        if capacity == 0 or capacity & (capacity - 1):
            print(f"Помилка: місткість {capacity} не є ступенем двійки", file=sys.stderr)
            return 2
        frames_raw = raw[HEADER_SIZE:]
        # У прошивці лічильник вільно росте; слот — це його молодші біти.
        head = header["sequence"] % capacity
        print("=" * 78)
        print(f"ЗВІТ БОРТОВОГО РЕЄСТРАТОРА: {path}")
        print(f"  запусків: {header['boots']}   аварій: {header['crashes']}   "
              f"подій усього: {header['sequence']}")
        print(f"  буфер: {capacity} кадрів   заморожено: "
              f"{'так' if header['frozen'] else 'ні'}   "
              f"заголовок: {'цілий' if header['crc_ok'] else 'ПОШКОДЖЕНО'}")
        print("=" * 78)

    available = len(frames_raw) // FRAME_SIZE
    if available < capacity:
        print(f"[!] у файлі лише {available} кадрів із {capacity} очікуваних", file=sys.stderr)
        capacity = available
        head = head % capacity if capacity else 0

    frames = [Frame(i, frames_raw[i * FRAME_SIZE:(i + 1) * FRAME_SIZE]) for i in range(capacity)]

    # Розкручування кільця: найдавніший запис лежить одразу за головою.
    ordered = frames[head:] + frames[:head]

    broken = 0
    shown = 0
    for frame in ordered:
        if frame.empty and not show_empty:
            continue
        if not frame.crc_ok:
            broken += 1

        subsystem = SUBSYSTEMS.get(frame.subsystem, f"0x{frame.subsystem:02X}")
        event = EVENTS.get(frame.event, f"0x{frame.event:02X}")
        status = "OK " if frame.crc_ok else "CRC"
        print(f"[{frame.timestamp:9d} мс] [{status}] [{subsystem:8s}] {event:14s} "
              f"FSM=0x{frame.fsm:04X}  {frame.payload.hex()}")
        for line in describe_fault(frame, resolver):
            print(line)
        shown += 1

    print("-" * 78)
    print(f"кадрів показано: {shown}   зіпсованих CRC: {broken}")
    if broken:
        # Побиті кадри — не привід ховати решту: саме заради цього кожен кадр
        # має власну контрольну суму, а не одна сума на весь буфер.
        print("[!] зіпсовані кадри лишено у звіті — їхній вміст читати не можна")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Декодер дампа бортового реєстратора")
    parser.add_argument("dump", help="двійковий файл, знятий зі слота FRAM або з .noinit")
    parser.add_argument("elf", nargs="?", default="", help="firmware.elf для розшифровки адрес")
    parser.add_argument("--toolchain", default="arm-none-eabi-",
                        help="префікс тулчейну (типово arm-none-eabi-)")
    parser.add_argument("--all", action="store_true", help="показувати й порожні слоти")
    args = parser.parse_args()

    try:
        return decode(args.dump, args.elf, args.toolchain, args.all)
    except OSError as error:
        print(f"Помилка читання: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
