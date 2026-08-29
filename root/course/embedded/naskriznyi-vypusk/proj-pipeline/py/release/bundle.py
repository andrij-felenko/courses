# -*- coding: utf-8 -*-
"""Ворота 4 і 6 — SBOM, маніфест бандла й детермінований архів."""
from __future__ import annotations

import gzip
import hashlib
import json
import tarfile
import uuid
from pathlib import Path

from .config import DEPENDENCIES, PRODUCT_ID, log

STAGE = "G6-BUNDLE"


def write_sbom(tag_info: dict, out_dir: Path) -> Path:
    """CycloneDX. Серійний номер виводиться з коміту, щоб два прогони одного
    тегу давали побайтово однаковий SBOM."""
    serial = uuid.uuid5(uuid.NAMESPACE_URL, f"urn:{PRODUCT_ID}:{tag_info['commit']}")
    sbom = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "serialNumber": f"urn:uuid:{serial}",
        "version": 1,
        "metadata": {
            "timestamp": tag_info["epoch"],
            "component": {
                "type": "firmware",
                "name": f"{PRODUCT_ID}-firmware",
                "version": tag_info["version_str"],
            },
        },
        "components": [
            {"type": "library", "name": name, "version": version, "purl": purl}
            for name, version, purl in DEPENDENCIES
        ],
    }
    path = out_dir / "firmware.sbom.json"
    _write_json(path, sbom)
    log("G4-SBOM", f"склад прошивки описано у {path.name} "
                   f"({len(DEPENDENCIES)} компонентів)")
    return path


def write_manifest(tag_info: dict, images: list[dict], out_dir: Path) -> Path:
    manifest = {
        "schema_version": "1.0",
        "product_id": PRODUCT_ID,
        "version": tag_info["version_str"],
        "commit": tag_info["commit"],
        "timestamp": tag_info["epoch"],
        "images": [
            {
                "hardware_target": rec["hardware_target"],
                "mcu": rec["mcu"],
                "hw_mask": rec["hw_mask"],
                "filename": rec["filename"],
                "filesize": rec["filesize"],
                "payload_size": rec["payload_size"],
                "payload_sha256": rec["payload_sha256"],
                "sha256": rec["sha256"],
                "security_counter": rec["security_counter"],
            }
            for rec in images
        ],
    }
    path = out_dir / "manifest.json"
    _write_json(path, manifest)
    log(STAGE, f"маніфест бандла: {path.name}, образів {len(images)}")
    return path


def pack_bundle(tag_info: dict, images: list[dict], extra: list[Path],
                out_dir: Path) -> Path:
    """Складає tar.gz, який побайтово однаковий на будь-якому раннері."""
    files = sorted([rec["path"] for rec in images] + list(extra),
                   key=lambda p: p.name)

    sums_path = out_dir / "SHA256SUMS"
    sums_path.write_text(
        "".join(f"{_sha256_file(path)}  {path.name}\n" for path in files),
        encoding="utf-8")
    files.append(sums_path)
    files.sort(key=lambda p: p.name)

    prefix = f"{PRODUCT_ID}-v{tag_info['version_str']}"
    archive = out_dir / f"{prefix}.tar.gz"

    def normalize(info: tarfile.TarInfo) -> tarfile.TarInfo:
        # Ім'я користувача, inode-порядок і час файлів — три джерела різниці
        # між двома прогонами. Прибиваємо всі три.
        info.uid = info.gid = 0
        info.uname = info.gname = ""
        info.mtime = tag_info["epoch"]
        info.mode = 0o644
        return info

    with open(archive, "wb") as raw:
        # mtime=0 у gzip: інакше час пакування лягає в шапку архіву.
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as gz:
            with tarfile.open(fileobj=gz, mode="w", format=tarfile.GNU_FORMAT) as tar:
                for path in files:
                    tar.add(path, arcname=f"{prefix}/{path.name}", filter=normalize)

    log(STAGE, f"бандл {archive.name}: {archive.stat().st_size} Б, "
               f"SHA-256 {_sha256_file(archive)[:16]}…")
    return archive


def _write_json(path: Path, payload: dict) -> None:
    # sort_keys — щоб порядок ключів не залежав від версії Python.
    text = json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True)
    path.write_text(text + "\n", encoding="utf-8")


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as src:
        for chunk in iter(lambda: src.read(64 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
