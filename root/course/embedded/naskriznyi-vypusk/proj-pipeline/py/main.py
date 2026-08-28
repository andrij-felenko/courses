#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
release_orchestrator.py — Наскрізний оркестратор випуску прошивки.
Виконується на раннері CI при спрацюванні тригера підписаного git-тегу.
"""

import os
import sys
import json
import hashlib
import subprocess
import argparse
from pathlib import Path
from datetime import datetime, timezone

# Список дозволених відбитків відкритих ключів GPG інженерів релізу
AUTHORIZED_RELEASE_KEY_FINGERPRINTS = {
    "9E8B7A6C5D4E3F2A1B0C9D8E7F6A5B4C3D2E1F0A",
    "1A2B3C4D5E6F7A8B9C0D1E2F3A4B5C6D7E8F9A0B"
}

# Апаратна матриця ревізій та ліміти Flash-пам'яті (у байтах)
HARDWARE_TARGETS = {
    "rev_B": {
        "mcu": "STM32G474RE",
        "preset": "prod-revB",
        "flash_limit": 262144,  # 256 KB під слот застосунку
        "hw_mask": 0x0002
    },
    "rev_C": {
        "mcu": "STM32G484RE",
        "preset": "prod-revC",
        "flash_limit": 524288,  # 512 KB
        "hw_mask": 0x0004
    }
}


def log(stage: str, msg: str) -> None:
    print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] [{stage}] {msg}")


def fail(stage: str, msg: str) -> None:
    print(f"\n❌ ПОМИЛКА НА ЕТАПІ [{stage}]: {msg}", file=sys.stderr)
    sys.exit(1)


def step_1_validate_git_tag(tag_name: str) -> dict:
    log("G1-TAG", f"Перевірка криптографічного тегу {tag_name}...")
    
    # 1. Перевірка статусу робочого дерева
    dirty = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    if dirty.stdout.strip():
        fail("G1-TAG", "Робоче дерево git містить непідтверджені зміни (dirty state)!")

    # 2. Перевірка підпису тегу
    verify = subprocess.run(["git", "tag", "-v", tag_name], capture_output=True, text=True)
    if verify.returncode != 0:
        fail("G1-TAG", f"Тег {tag_name} не має дійсного цифрового підпису GPG/SSH!\n{verify.stderr}")

    # 3. Розбір семантичної версії vMAJOR.MINOR.PATCH
    if not tag_name.startswith("v"):
        fail("G1-TAG", "Ім'я тегу має починатися з префіксу 'v' (наприклад, v2.4.0)")
    
    ver_clean = tag_name[1:]
    parts = ver_clean.split(".")
    if len(parts) != 3 or not all(p.isdigit() for p in parts):
        fail("G1-TAG", f"Версія '{ver_clean}' не відповідає формату SemVer (MAJOR.MINOR.PATCH)")

    # 4. Отримання мітки часу коміту для SOURCE_DATE_EPOCH
    ts = subprocess.run(["git", "log", "-1", "--format=%ct", tag_name], capture_output=True, text=True)
    commit_hash = subprocess.run(["git", "log", "-1", "--format=%H", tag_name], capture_output=True, text=True)
    
    epoch_ts = int(ts.stdout.strip())
    log("G1-TAG", f"Валідовано: версія {ver_clean}, коміт {commit_hash.stdout.strip()[:8]}, епоха {epoch_ts}")

    return {
        "version_str": ver_clean,
        "major": int(parts[0]),
        "minor": int(parts[1]),
        "patch": int(parts[2]),
        "commit": commit_hash.stdout.strip(),
        "epoch": epoch_ts
    }


def step_2_build_matrix(tag_info: dict, out_dir: Path) -> dict:
    log("G2-BUILD", "Запуск герметичної матричної збірки...")
    
    # Встановлення змінних середовища детермінізму
    env = os.environ.copy()
    env["SOURCE_DATE_EPOCH"] = str(tag_info["epoch"])
    env["LC_ALL"] = "C"

    built_images = {}

    for hw_name, target in HARDWARE_TARGETS.items():
        log("G2-BUILD", f"Збирання цілі {hw_name} ({target['mcu']}) з пресетом {target['preset']}...")
        
        build_path = out_dir / f"build_{hw_name}"
        build_path.mkdir(parents=True, exist_ok=True)

        # Конфігурація CMake
        cfg_cmd = [
            "cmake", "--preset", target["preset"],
            f"-DFW_VERSION_MAJOR={tag_info['major']}",
            f"-DFW_VERSION_MINOR={tag_info['minor']}",
            f"-DFW_VERSION_PATCH={tag_info['patch']}",
            f"-DFW_COMMIT_HASH=0x{tag_info['commit'][:8]}"
        ]
        res = subprocess.run(cfg_cmd, cwd=Path.cwd(), env=env)
        if res.returncode != 0:
            fail("G2-BUILD", f"Помилка конфігурації CMake для {hw_name}")

        # Компіляція бінарників
        build_cmd = ["cmake", "--build", f"--preset", target["preset"]]
        res = subprocess.run(build_cmd, cwd=Path.cwd(), env=env)
        if res.returncode != 0:
            fail("G2-BUILD", f"Помилка компіляції прошивки для {hw_name}")

        raw_bin = build_path / f"app-{hw_name}.raw.bin"
        elf_file = build_path / f"app-{hw_name}.elf"
        
        if not raw_bin.exists():
            fail("G2-BUILD", f"Цільовий бінарник {raw_bin} не згенеровано")

        # Перевірка бюджету пам'яті
        size_bytes = raw_bin.stat().st_size
        log("G2-BUILD", f"Розмір {raw_bin.name}: {size_bytes} байтів (ліміт: {target['flash_limit']} байтів)")
        
        if size_bytes > target["flash_limit"]:
            fail("G2-BUILD", f"ПРОБИТО БЮДЖЕТ ПАМ'ЯТІ! {size_bytes} > {target['flash_limit']}")

        built_images[hw_name] = {
            "raw_bin": raw_bin,
            "elf": elf_file,
            "size": size_bytes,
            "target_info": target
        }

    return built_images


def step_3_mock_hsm_sign(digest_bytes: bytes, key_id: str) -> bytes:
    """
    Симуляція взаємодії з апаратним модулем HSM / AWS KMS через PKCS#11 API.
    Приймає лише 32-байтний SHA-256 хеш і повертає 64-байтний підпис ECDSA/Ed25519.
    """
    log("G4-SIGN", f"Надсилання дайджесту ({digest_bytes.hex()[:16]}...) до HSM [Ключ: {key_id}]")
    
    # У виробництві тут виконується виклик pkcs11-tool або aws kms sign --digest ...
    # Для демонстрації генеруємо детермінований HMAC-підпис від дайджесту
    sig_engine = hashlib.sha512()
    sig_engine.update(b"MOCK_HSM_PROTECTED_PRODUCTION_ROOT_KEY_2026")
    sig_engine.update(digest_bytes)
    return sig_engine.digest()[:64]


def step_4_package_and_sign(tag_info: dict, built_images: dict, out_dir: Path) -> Path:
    log("G4-PACKAGE", "Накладання цифрових підписів і формування заголовків Secure Boot...")
    
    bundle_manifest = {
        "schema_version": "1.0",
        "product_id": "iot-sensor-node",
        "version": tag_info["version_str"],
        "commit": tag_info["commit"],
        "timestamp": tag_info["epoch"],
        "images": []
    }

    SECURE_BOOT_MAGIC = 0x53424F54  # "SBOT"

    for hw_name, img in built_images.items():
        raw_bin_path = img["raw_bin"]
        signed_bin_path = out_dir / f"firmware-{hw_name}-v{tag_info['version_str']}.signed.bin"
        
        with open(raw_bin_path, "rb") as f:
            payload = f.read()

        payload_digest = hashlib.sha256(payload).digest()

        # Формування бінарного заголовка (128 байтів)
        security_counter = 3  # Anti-rollback лічильник
        hw_mask = img["target_info"]["hw_mask"]
        payload_size = len(payload)

        header_bytes = bytearray(128)
        header_bytes[0:4] = SECURE_BOOT_MAGIC.to_bytes(4, "little")
        header_bytes[4:8] = ((tag_info["major"] << 24) | (tag_info["minor"] << 16) | (tag_info["patch"] << 8)).to_bytes(4, "little")
        header_bytes[8:12] = security_counter.to_bytes(4, "little")
        header_bytes[12:16] = hw_mask.to_bytes(4, "little")
        header_bytes[16:20] = payload_size.to_bytes(4, "little")
        header_bytes[20:52] = payload_digest

        # Підпис хешу заголовка + тіла через HSM
        header_and_body_digest = hashlib.sha256(header_bytes[:52] + payload).digest()
        signature = step_3_mock_hsm_sign(header_and_body_digest, key_id="prod-firmware-signer-v1")
        header_bytes[52:116] = signature

        # Запис повного підписаного образу (Header + Payload)
        with open(signed_bin_path, "wb") as f:
            f.write(header_bytes)
            f.write(payload)

        final_sha256 = hashlib.sha256(header_bytes + payload).hexdigest()
        log("G4-PACKAGE", f"Створено підписаний образ: {signed_bin_path.name} (SHA256: {final_sha256[:16]}...)")

        bundle_manifest["images"].append({
            "hardware_target": hw_name,
            "filename": signed_bin_path.name,
            "filesize": len(header_bytes) + len(payload),
            "sha256": final_sha256,
            "security_counter": security_counter
        })

    # Запис маніфесту
    manifest_file = out_dir / "manifest.json"
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(bundle_manifest, f, indent=2)

    # Генерація спрощеного SBOM
    sbom_file = out_dir / "firmware.sbom.json"
    sbom_content = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "version": 1,
        "metadata": {
            "component": {
                "name": "iot-sensor-firmware",
                "version": tag_info["version_str"],
                "type": "firmware"
            }
        },
        "components": [
            {"name": "FreeRTOS-Kernel", "version": "10.5.1", "purl": "pkg:github/FreeRTOS/FreeRTOS-Kernel@V10.5.1"},
            {"name": "mbedTLS", "version": "3.4.0", "purl": "pkg:github/Mbed-TLS/mbedtls@v3.4.0"},
            {"name": "STM32G4-HAL", "version": "1.5.0", "purl": "pkg:github/STMicroelectronics/STM32CubeG4@v1.5.0"}
        ]
    }
    with open(sbom_file, "w", encoding="utf-8") as f:
        json.dump(sbom_content, f, indent=2)

    log("G5-SBOM", f"Згенеровано маніфест і SBOM у {out_dir}")
    return manifest_file


def main():
    parser = argparse.ArgumentParser(description="Оркестратор випуску прошивки")
    parser.add_argument("--tag", required=True, help="Ім'я підписаного git-тегу (наприклад, v2.4.0)")
    parser.add_argument("--out", default="./dist", help="Цільовий каталог для релізного бандла")
    args = parser.parse_args()

    out_dir = Path(args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    log("INIT", "=== ПОЧАТОК НАСКРІЗНОГО ВИПУСКУ ПРОШИВКИ ===")
    
    # Крок 1: Валідація тегу
    tag_info = step_1_validate_git_tag(args.tag)
    
    # Крок 2: Матрична збірка
    built_images = step_2_build_matrix(tag_info, out_dir)
    
    # Крок 3: Підпис та упаковка
    step_4_package_and_sign(tag_info, built_images, out_dir)
    
    log("COMPLETE", "✅ НАСКРІЗНИЙ ВИПУСК УСПІШНО ЗАВЕРШЕНО! Артефакти готові до публікації.")


if __name__ == "__main__":
    main()
