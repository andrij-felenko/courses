#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
release_orchestrator.py — наскрізний оркестратор випуску прошивки.

Запускається на раннері CI за подією підписаного git-тегу:

    python3 scripts/release_orchestrator.py --tag v2.4.0 --out ./release_dist

Шість воріт поспіль: тег → матрична збірка → бюджет Flash → SBOM → підпис
у HSM → бандл. Провал будь-яких воріт термінальний: тимчасові файли зносяться,
недороблений каталог випуску теж, причина йде у stderr, код повернення 1.
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from release import build, bundle, gitgate, hsm, image
from release.config import ReleaseError, log


def run_pipeline(tag: str, out_dir: Path, work_dir: Path) -> Path:
    """Послідовність воріт. Будь-яке кидає ReleaseError — і на цьому все."""
    tag_info = gitgate.step_1_validate_git_tag(tag)          # ворота 1
    built = build.step_2_build_matrix(tag_info, work_dir)    # ворота 2 і 3
    sbom_path = bundle.write_sbom(tag_info, out_dir)         # ворота 4
    signed = image.package_images(tag_info, built, out_dir)  # ворота 5
    manifest_path = bundle.write_manifest(tag_info, signed, out_dir)

    extra = [manifest_path, sbom_path]
    pubkey_path = hsm.export_public_key(out_dir / "root-pubkey.bin")
    if pubkey_path is not None:
        extra.append(pubkey_path)

    return bundle.pack_bundle(tag_info, signed, extra, out_dir)  # ворота 6


def main() -> int:
    parser = argparse.ArgumentParser(description="Оркестратор випуску прошивки")
    parser.add_argument("--tag", required=True,
                        help="ім'я підписаного git-тегу, наприклад v2.4.0")
    parser.add_argument("--out", default="./dist",
                        help="каталог релізного бандла (створюється наново)")
    args = parser.parse_args()

    out_dir = Path(args.out).resolve()
    work_dir = out_dir / ".work"

    # Каталог випуску мусить бути порожній: залишки попереднього прогону
    # інакше мовчки поїдуть в артефакт разом зі свіжими файлами.
    if out_dir.exists():
        shutil.rmtree(out_dir)
    work_dir.mkdir(parents=True)

    log("INIT", f"=== наскрізний випуск {args.tag} → {out_dir} ===")

    try:
        archive = run_pipeline(args.tag, out_dir, work_dir)
    except ReleaseError as err:
        print(f"\nПОМИЛКА НА ЕТАПІ [{err.stage}]: {err.msg}", file=sys.stderr)
        shutil.rmtree(out_dir, ignore_errors=True)
        return 1
    except KeyboardInterrupt:
        print("\nПерервано оператором — каталог випуску знесено.", file=sys.stderr)
        shutil.rmtree(out_dir, ignore_errors=True)
        return 130

    shutil.rmtree(work_dir, ignore_errors=True)
    log("DONE", f"бандл готовий: {archive.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
