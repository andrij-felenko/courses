"""Стендова утиліта: зібрати кадр, розібрати кадр, просіяти дамп потоку.

    python -m telemetry emit telemetry --temperature 24.5 --pressure 1013.2 \
        --voltage 3300 --alert --seq 0x4A
    python -m telemetry decode AA 01 20 4A 08 00 …
    python -m telemetry scan --file capture.bin --chunk 7

Розбір полів робить згенерований парсер. Якщо його ще не згенеровано,
команда decode чесно каже це й показує саму лише перевірку конверта —
рамкування й CRC від ksc не залежать.
"""

from __future__ import annotations

import argparse
import sys
from typing import Any, Sequence

from .decoder import DecodedFrame, check_envelope, decode
from .encoder import Ack, Ping, SetConfig, Telemetry, build_frame
from .errors import ProtocolError
from .framer import FrameReader, read_frames
from .wire import MsgType, StatusCode


def _hex(data: bytes) -> str:
    return " ".join(f"{byte:02X}" for byte in data)


def _parse_hex(tokens: Sequence[str]) -> bytes:
    """Приймає і "AA 01 20", і "aa012 0", і "0xAA,0x01" — з логів беруть по-різному."""
    cleaned = "".join(tokens).replace("0x", "").replace(",", "").replace(":", "")
    cleaned = "".join(ch for ch in cleaned if not ch.isspace())
    if len(cleaned) % 2:
        raise argparse.ArgumentTypeError(f"непарне число шістнадцяткових цифр: {len(cleaned)}")
    try:
        return bytes.fromhex(cleaned)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"не шістнадцятковий дамп: {exc}") from exc


def _int0(text: str) -> int:
    """0x4A, 0b101 і 74 — усе одне й те саме число."""
    return int(text, 0)


def describe_payload(packet: Any, msg_type: MsgType) -> list[str]:
    """Поля навантаження так, як їх віддав згенерований парсер."""
    payload = packet.payload
    match msg_type:
        case MsgType.TELEMETRY_REPORT:
            return [
                f"  temp_raw={payload.temp_raw} -> {payload.temperature_c:.2f} °C",
                f"  pressure_raw={payload.pressure_raw} -> {payload.pressure_hpa:.1f} гПа",
                f"  voltage_mv={payload.voltage_mv}",
                f"  flags=0x{payload.flags:02X} alert={payload.alert_active} "
                f"fault={payload.sensor_fault}",
            ]
        case MsgType.CMD_SET_CONFIG:
            return [
                f"  sample_rate_hz={payload.sample_rate_hz}",
                f"  alert_threshold_raw={payload.alert_threshold_raw} -> "
                f"{payload.alert_threshold_c:.2f} °C",
                f"  flags_enable=0x{payload.flags_enable:02X}",
            ]
        case MsgType.CMD_RESPONSE:
            return [
                f"  target_seq_id=0x{payload.target_seq_id:02X}",
                f"  status={payload.status}",
            ]
        case MsgType.CMD_PING:
            return ["  навантаження немає"]
    return [f"  сирі байти: {_hex(bytes(payload))}"]


def describe(frame: bytes) -> list[str]:
    """Один кадр у людський вигляд; порожній список — кадр відкинуто."""
    envelope = check_envelope(frame)
    lines = [
        f"{envelope.msg_type.name}  version={envelope.version} "
        f"seq=0x{envelope.seq_id:02X} len={envelope.payload_len} "
        f"crc=0x{envelope.crc16:04X}",
    ]
    try:
        decoded: DecodedFrame = decode(frame)
    except RuntimeError as exc:
        lines.append(f"  (поля не розібрано: {exc})")
        lines.append(f"  сирий payload: {_hex(envelope.payload)}")
        return lines
    lines.extend(describe_payload(decoded.packet, envelope.msg_type))
    return lines


def cmd_emit(args: argparse.Namespace) -> int:
    match args.kind:
        case "telemetry":
            payload = Telemetry.from_physical(
                temperature_c=args.temperature,
                pressure_hpa=args.pressure,
                voltage_mv=args.voltage,
                alert=args.alert,
                fault=args.fault,
            )
        case "set-config":
            payload = SetConfig.from_physical(
                sample_rate_hz=args.rate,
                alert_threshold_c=args.threshold,
                flags_enable=args.flags,
            )
        case "ack":
            payload = Ack(target_seq_id=args.target, status=StatusCode[args.status.upper()])
        case _:
            payload = Ping()

    frame = build_frame(payload, seq_id=args.seq)
    if args.out:
        args.out.write_bytes(frame)
    print(_hex(frame))
    return 0


def cmd_decode(args: argparse.Namespace) -> int:
    frame = args.file.read_bytes() if args.file else _parse_hex(args.hex)
    try:
        for line in describe(frame):
            print(line)
    except ProtocolError as exc:
        print(f"кадр відкинуто: {exc}", file=sys.stderr)
        return 1
    return 0


def cmd_scan(args: argparse.Namespace) -> int:
    reader = FrameReader()
    found = 0
    with args.file.open("rb") as stream:
        for frame in read_frames(reader, stream, chunk_size=args.chunk):
            found += 1
            print(f"[{found}] {_hex(frame)}")
            try:
                for line in describe(frame):
                    print(f"    {line}")
            except ProtocolError as exc:  # pragma: no cover — рамкувальник уже перевірив суму
                print(f"    кадр відкинуто: {exc}")
    stats = reader.stats.as_dict()
    print("статистика: " + ", ".join(f"{key}={value}" for key, value in stats.items()))
    if reader.pending:
        print(f"недобраний хвіст: {reader.pending} байт")
    return 0 if found else 1


def build_parser() -> argparse.ArgumentParser:
    import pathlib

    parser = argparse.ArgumentParser(prog="telemetry", description=__doc__.splitlines()[0])
    subs = parser.add_subparsers(dest="command", required=True)

    emit = subs.add_parser("emit", help="зібрати кадр і надрукувати його байти")
    emit.add_argument("kind", choices=["telemetry", "set-config", "ack", "ping"])
    emit.add_argument("--seq", type=_int0, default=0x00)
    emit.add_argument("--temperature", type=float, default=24.5)
    emit.add_argument("--pressure", type=float, default=1013.2)
    emit.add_argument("--voltage", type=_int0, default=3300)
    emit.add_argument("--alert", action="store_true")
    emit.add_argument("--fault", action="store_true")
    emit.add_argument("--rate", type=_int0, default=100)
    emit.add_argument("--threshold", type=float, default=85.0)
    emit.add_argument("--flags", type=_int0, default=0x03)
    emit.add_argument("--target", type=_int0, default=0x10)
    emit.add_argument(
        "--status", choices=[code.name.lower() for code in StatusCode], default="ok"
    )
    emit.add_argument("--out", type=pathlib.Path, help="записати кадр ще й у файл")
    emit.set_defaults(func=cmd_emit)

    dec = subs.add_parser("decode", help="розібрати один кадр")
    dec.add_argument("hex", nargs="*", help="шістнадцятковий дамп кадру")
    dec.add_argument("--file", type=pathlib.Path, help="кадр у двійковому файлі")
    dec.set_defaults(func=cmd_decode)

    scan = subs.add_parser("scan", help="просіяти дамп потоку рамкувальником")
    scan.add_argument("--file", type=pathlib.Path, required=True)
    scan.add_argument("--chunk", type=int, default=64, help="розмір шматка читання")
    scan.set_defaults(func=cmd_scan)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "decode" and not args.hex and not args.file:
        parser.error("подай дамп кадру або --file")
    try:
        return int(args.func(args))
    except (ValueError, TypeError) as exc:
        print(f"помилка: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
