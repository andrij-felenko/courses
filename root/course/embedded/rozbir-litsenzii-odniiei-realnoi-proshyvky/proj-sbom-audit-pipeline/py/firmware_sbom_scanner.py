#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ліцензійний шлюз конвеєра збірки прошивки.

    python3 scripts/firmware_sbom_scanner.py build/firmware.map build/firmware.bin

Крок ставлять одразу після лінкування й ПЕРЕД підписом образу. Коди виходу —
контракт із CI, тому вони фіксовані:

    0 — склад образу відповідає політиці, паспорт і файл атрибуції записано;
    1 — аудит не відбувся (немає мапи, битий конфіг, не запустився nm у --strict);
    2 — ЛІЦЕНЗІЙНЕ ПОРУШЕННЯ: у Flash код під забороненою ліцензією;
    3 — є зауваження, а прогін запущено з --strict.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

from sbom_audit import TOOL_NAME, TOOL_VERSION
from sbom_audit.catalog import Catalog, CatalogError
from sbom_audit.linkmap import MapError, parse_map
from sbom_audit.report import build_sbom, write_notice, write_sbom
from sbom_audit.symbols import NmError, audit_symbols, collect_defined_symbols

EXIT_OK, EXIT_SETUP, EXIT_LICENSE, EXIT_STRICT = 0, 1, 2, 3

DEFAULT_CONFIG = Path(__file__).resolve().parent / "components.json"


def sha256_of(path: Path) -> str:
    """Хеш образу читаємо блоками: firmware.bin буває й на кілька мегабайт."""

    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_args(argv: list[str]) -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        prog="firmware_sbom_scanner",
        description="Пост-лінкерний ліцензійний аудит і генерація SBOM для прошивки MCU",
    )
    ap.add_argument("map_file", help="мапа компонувальника (-Wl,-Map=build/firmware.map)")
    ap.add_argument("bin_file", help="фінальний образ, що піде на підпис і в OTA")
    ap.add_argument("--elf", help="ELF для звірки через nm (типово <bin>.elf поруч)")
    ap.add_argument("--config", default=str(DEFAULT_CONFIG), help="база компонентів (JSON)")
    ap.add_argument("--nm", default="arm-none-eabi-nm", help="утиліта nm із тулчейна")
    ap.add_argument("--sbom-out", help="куди писати CycloneDX (типово <bin>.cdx.json)")
    ap.add_argument("--notice-out", help="куди писати THIRD_PARTY_LICENSES.txt")
    ap.add_argument("--strict", action="store_true",
                    help="будь-яке зауваження валить збірку (нічні та релізні прогони)")
    return ap.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    bin_path = Path(args.bin_file)

    # --- крок 1: конфіг, мапа, хеш образу -----------------------------------
    try:
        catalog = Catalog.load(args.config)
        report = parse_map(args.map_file)
        binary_hash = sha256_of(bin_path)
    except (CatalogError, MapError) as exc:
        print(f"[АУДИТ НЕ ВІДБУВСЯ] {exc}", file=sys.stderr)
        return EXIT_SETUP
    except FileNotFoundError:
        print(f"[АУДИТ НЕ ВІДБУВСЯ] немає образу: {bin_path}", file=sys.stderr)
        return EXIT_SETUP
    except OSError as exc:
        print(f"[АУДИТ НЕ ВІДБУВСЯ] {bin_path}: {exc}", file=sys.stderr)
        return EXIT_SETUP

    detections, findings = catalog.attribute(report)

    print(f"{TOOL_NAME} {TOOL_VERSION}: у образі {report.total_bytes} Б коду й даних "
          f"з {len(report.objects)} модулів "
          f"(--gc-sections викинув {report.gc_dropped_sections} секцій)")
    print(f"SHA-256 {binary_hash}\n")

    print(f"{'Компонент':<34} {'Версія':<10} {'Ліцензія':<28} {'Байт':>8}  Модулів")
    print("-" * 96)
    for det in sorted(detections.values(), key=lambda d: -d.size):
        comp = det.component
        print(f"{comp.name[:33]:<34} {comp.version[:9]:<10} "
              f"{comp.license_text[:27]:<28} {det.size:>8}  {len(det.objects)}")
    print("-" * 96)

    # --- крок 2: шлюз політики ----------------------------------------------
    # Порушення закриває конвеєр ДО генерації артефактів: паспорт на образ,
    # який не має права їхати до замовника, нікому не потрібен.
    violations = catalog.violations(detections)
    if violations:
        print("\n[ПОМИЛКА ЛІЦЕНЗІЙНОГО ШЛЮЗУ] у прошивці код під забороненою ліцензією:",
              file=sys.stderr)
        for item in violations:
            print(f"  x {item}", file=sys.stderr)
        print("  Підпис образу заблоковано.", file=sys.stderr)
        return EXIT_LICENSE

    # --- крок 3: перехресна звірка таблиці символів --------------------------
    elf_path = Path(args.elf) if args.elf else bin_path.with_suffix(".elf")
    symbol_findings = []
    if elf_path.is_file():
        try:
            symbols = collect_defined_symbols(elf_path, nm_tool=args.nm)
            symbol_findings = audit_symbols(
                symbols,
                watch_prefixes=catalog.watch_prefixes,
                declared_prefixes=catalog.declared_prefixes(),
                detected_ids=set(detections),
            )
            print(f"\nЗвірено {len(symbols)} визначених символів через {args.nm}")
        except NmError as exc:
            if args.strict:
                print(f"[АУДИТ НЕ ВІДБУВСЯ] звірка символів: {exc}", file=sys.stderr)
                return EXIT_SETUP
            print(f"\n[УВАГА] звірку символів пропущено: {exc}")
    else:
        print(f"\n[УВАГА] {elf_path} немає — звірку таблиці символів пропущено")

    # --- крок 4: артефакти ---------------------------------------------------
    sbom_path = Path(args.sbom_out) if args.sbom_out else bin_path.with_suffix(".cdx.json")
    notice_path = (Path(args.notice_out) if args.notice_out
                   else bin_path.parent / "THIRD_PARTY_LICENSES.txt")
    try:
        document = build_sbom(catalog, detections, binary_hash, bin_path.name)
        write_sbom(sbom_path, document)
        write_notice(notice_path, catalog, detections, binary_hash)
    except OSError as exc:
        print(f"[АУДИТ НЕ ВІДБУВСЯ] артефакти не записалися: {exc}", file=sys.stderr)
        return EXIT_SETUP

    # --- крок 5: зауваження --------------------------------------------------
    warnings = [f for f in findings if f.severity == "warning"]
    notes = [f for f in findings if f.severity == "info"]

    for finding in notes:
        print(f"  · {finding.code}: {finding.message}")
    for finding in warnings:
        print(f"  ! {finding.code}: {finding.message}")
    for finding in symbol_findings:
        print(f"  ! {finding.code}: {finding.message}")

    print(f"\n[ГОТОВО] компонентів: {len(detections)}; SBOM: {sbom_path}; "
          f"атрибуція: {notice_path}")

    blocking = len(warnings) + len(symbol_findings)
    if blocking and args.strict:
        print(f"[STRICT] зауважень {blocking} — збірку зупинено", file=sys.stderr)
        return EXIT_STRICT
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
