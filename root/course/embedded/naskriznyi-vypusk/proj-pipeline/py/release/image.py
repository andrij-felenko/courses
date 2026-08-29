# -*- coding: utf-8 -*-
"""Заголовок Secure Boot і збирання підписаного образу.

Розкладка 128 байтів (усе — little-endian, як його читає Cortex-M):

    0   magic            "SBOT"
    4   version_packed   major<<24 | minor<<16 | patch<<8
    8   security_counter anti-rollback
    12  hw_mask          маска сумісних ревізій
    16  payload_size     довжина тіла
    20  payload_sha256   32 Б
    52  signature        64 Б, ECDSA P-256 над SHA-256(заголовок[0:52] || тіло)
    116 reserved         12 Б нулів
"""
from __future__ import annotations

import hashlib
from pathlib import Path

from . import hsm
from .config import (DIGEST_LEN, HEADER_SIZE, SECURE_BOOT_MAGIC, SECURITY_COUNTER,
                     SIGNATURE_LEN, SIGNED_PREFIX_LEN, SIGNING_KEY_ID, fail, log)

STAGE = "G4-IMAGE"


def pack_version(major: int, minor: int, patch: int) -> int:
    return (major << 24) | (minor << 16) | (patch << 8)


def build_header(tag_info: dict, hw_mask: int, payload: bytes) -> bytearray:
    """Заголовок без підпису: байти 0..51 уже остаточні."""
    header = bytearray(HEADER_SIZE)
    header[0:4] = SECURE_BOOT_MAGIC.to_bytes(4, "little")
    header[4:8] = pack_version(tag_info["major"], tag_info["minor"],
                               tag_info["patch"]).to_bytes(4, "little")
    header[8:12] = SECURITY_COUNTER.to_bytes(4, "little")
    header[12:16] = hw_mask.to_bytes(4, "little")
    header[16:20] = len(payload).to_bytes(4, "little")
    header[20:52] = hashlib.sha256(payload).digest()
    return header


def package_images(tag_info: dict, built: dict, out_dir: Path) -> list[dict]:
    """Для кожної цілі: заголовок → дайджест → HSM → підписаний образ."""
    log(STAGE, "накладання заголовків Secure Boot і цифрових підписів…")
    records: list[dict] = []

    for hw_name, item in built.items():
        payload = item["raw_bin"].read_bytes()
        if len(payload) >= 1 << 32:
            fail(STAGE, f"тіло {hw_name} не влазить у 32-бітне поле розміру")

        header = build_header(tag_info, item["target"]["hw_mask"], payload)

        # Підписуємо саме заголовок разом із тілом: інакше зловмисник
        # переставив би підписане тіло під чужий заголовок і збив маску
        # сумісності чи лічильник відкату.
        signed_digest = hashlib.sha256(bytes(header[:SIGNED_PREFIX_LEN]) + payload).digest()
        signature = hsm.step_3_mock_hsm_sign(signed_digest, SIGNING_KEY_ID)
        header[52:52 + SIGNATURE_LEN] = signature

        name = f"firmware-{hw_name}-v{tag_info['version_str']}.signed.bin"
        path = out_dir / name
        with open(path, "wb") as out:
            out.write(header)
            out.write(payload)

        image_sha = hashlib.sha256(bytes(header) + payload).hexdigest()
        log(STAGE, f"{name}: {len(header) + len(payload)} Б, SHA-256 {image_sha[:16]}…")

        records.append({
            "hardware_target": hw_name,
            "mcu": item["target"]["mcu"],
            "hw_mask": item["target"]["hw_mask"],
            "path": path,
            "filename": name,
            "filesize": len(header) + len(payload),
            "payload_size": len(payload),
            "payload_sha256": header[20:20 + DIGEST_LEN].hex(),
            "sha256": image_sha,
            "security_counter": SECURITY_COUNTER,
        })

    return records
