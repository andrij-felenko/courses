#!/usr/bin/env python3
"""
firmware_packager.py — Утиліта формування підписаного пакета випуску прошивки.
"""

import struct
import hashlib
import argparse
import sys
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import ed25519

MAGIC_WORD = 0x46574D46      # "FWMF"
HEADER_VERSION = 1
HEADER_FORMAT_NO_SIG = "<IIIBBHBBBBII32s" # 64 байти метаданих без підпису

def create_release_package(
    payload_path: Path,
    output_path: Path,
    privkey_path: Path,
    target_hw_id: int,
    hw_rev_min: int,
    hw_rev_max: int,
    ver_major: int,
    ver_minor: int,
    ver_patch: int,
    security_version: int,
    load_address: int
) -> None:
    # 1. Зчитування корисного навантаження
    payload_data = payload_path.read_bytes()
    payload_size = len(payload_data)
    if payload_size == 0:
        raise ValueError("Файл корисного навантаження порожній")

    # 2. Обчислення SHA-256 дайджесту образу
    hasher = hashlib.sha256()
    hasher.update(payload_data)
    payload_sha256 = hasher.digest()

    # 3. Формування перших 64 байтів бінарного заголовка
    flags = 0
    ver_pre_flags = 0 # 0 = release
    header_raw_64 = struct.pack(
        HEADER_FORMAT_NO_SIG,
        MAGIC_WORD,
        HEADER_VERSION,
        target_hw_id,
        hw_rev_min,
        hw_rev_max,
        flags,
        ver_major,
        ver_minor,
        ver_patch,
        ver_pre_flags,
        security_version,
        payload_size,
        load_address,
        payload_sha256
    )

    if len(header_raw_64) != 64:
        raise RuntimeError(f"Помилка упаковки: очікувалось 64 байти, отримано {len(header_raw_64)}")

    # 4. Накладання криптографічного підпису Ed25519
    with open(privkey_path, "rb") as kf:
        private_key = ed25519.Ed25519PrivateKey.from_private_bytes(kf.read()[:32])

    signature_bytes = private_key.sign(header_raw_64)
    if len(signature_bytes) != 64:
        raise RuntimeError(f"Некоректний розмір підпису Ed25519: {len(signature_bytes)}")

    # 5. Складання повного 128-байтного заголовка
    complete_header = header_raw_64 + signature_bytes
    if len(complete_header) != 128:
        raise RuntimeError("Повний заголовок не дорівнює 128 байтам")

    # 6. Запис фінального релізного пакета
    with open(output_path, "wb") as out_f:
        out_f.write(complete_header)
        out_f.write(payload_data)

    print(f"✓ Реліз успішно зібрано: {output_path}")
    print(f"  Розмір коду: {payload_size} байтів")
    print(f"  SemVer: {ver_major}.{ver_minor}.{ver_patch}")
    print(f"  Security Version: {security_version}")
    print(f"  SHA-256: {payload_sha256.hex()}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Пакувальник релізу вбудованої прошивки")
    parser.add_argument("--payload", required=True, type=Path, help="Шлях до файлу firmware.bin")
    parser.add_argument("--key", required=True, type=Path, help="Файл закритого ключа Ed25519")
    parser.add_argument("--out", required=True, type=Path, help="Цільовий файл пакету .fwpkg")
    parser.add_argument("--hw-id", required=True, type=lambda x: int(x, 0), help="Ідентифікатор плати (напр. 0xA1F0)")
    parser.add_argument("--rev-min", default=1, type=int, help="Мінімальна ревізія PCB")
    parser.add_argument("--rev-max", default=3, type=int, help="Максимальна ревізія PCB")
    parser.add_argument("--ver", required=True, help="Версія у форматі X.Y.Z")
    parser.add_argument("--sec-ver", required=True, type=int, help="Індекс anti-rollback")
    parser.add_argument("--load-addr", default="0x08020000", type=lambda x: int(x, 0), help="Адреса завантаження")

    args = parser.parse_args()
    v_maj, v_min, v_patch = map(int, args.ver.split("."))
    create_release_package(
        args.payload, args.out, args.key, args.hw_id,
        args.rev_min, args.rev_max, v_maj, v_min, v_patch,
        args.sec_ver, args.load_addr
    )
