#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""firmware_sbom_scanner.py — пост-лінкерний аудит ліцензій для MCU"""

import re
import sys
import json
import hashlib
from pathlib import Path

# База метаданих сторонніх компонентів проєкту
COMPONENT_DATABASE = {
    "freertos": {
        "name": "FreeRTOS Kernel",
        "version": "10.5.1",
        "license_spdx": "MIT",
        "purl": "pkg:generic/freertos@10.5.1",
        "supplier": "Amazon Web Services",
        "pattern": r"(freertos|tasks\.o|queue\.o|list\.o|port\.o)"
    },
    "lwip": {
        "name": "lwIP - Lightweight IP stack",
        "version": "2.2.0",
        "license_spdx": "BSD-3-Clause",
        "purl": "pkg:generic/lwip@2.2.0",
        "supplier": "Swedish Institute of Computer Science",
        "pattern": r"(lwip|tcp\.o|udp\.o|ip4\.o|ethernet\.o|pbuf\.o)"
    },
    "mbedtls": {
        "name": "mbed TLS",
        "version": "3.4.1",
        "license_spdx": "Apache-2.0",
        "purl": "pkg:generic/mbedtls@3.4.1",
        "supplier": "TrustedFirmware.org",
        "pattern": r"(mbedtls|aes\.o|sha256\.o|ssl_tls\.o|x509\.o)"
    },
    "fatfs": {
        "name": "FatFS",
        "version": "R0.15",
        "license_spdx": "FatFS-Permissive",
        "purl": "pkg:generic/fatfs@R0.15",
        "supplier": "ChaN",
        "pattern": r"(ff\.o|diskio\.o|ffsystem\.o|ffunicode\.o)"
    },
    "cmsis_core": {
        "name": "ARM CMSIS Core",
        "version": "5.9.0",
        "license_spdx": "Apache-2.0",
        "purl": "pkg:generic/arm-cmsis@5.9.0",
        "supplier": "Arm Limited",
        "pattern": r"(system_stm32|cmsis|core_cm7\.o)"
    },
    "stm32_hal": {
        "name": "STM32CubeH7 HAL Drivers",
        "version": "1.11.0",
        "license_spdx": "BSD-3-Clause",
        "purl": "pkg:generic/stm32cube-hal@1.11.0",
        "supplier": "STMicroelectronics",
        "pattern": r"(stm32h7xx_hal|stm32h7xx_ll)"
    },
    "vendor_phy_blob": {
        "name": "Vendor Wi-Fi PHY Driver (Binary Blob)",
        "version": "2.4.18",
        "license_spdx": "Proprietary-Vendor-EULA",
        "purl": "pkg:generic/vendor-phy-blob@2.4.18",
        "supplier": "Silicon Vendor Corp",
        "pattern": r"(libphy_wifi\.a|libcoexist\.a)"
    }
}

# Політика ліцензійної відповідності для комерційного пристрою
BANNED_LICENSES = {"GPL-2.0-only", "GPL-2.0-or-later", "GPL-3.0-only", "GPL-3.0-or-later", "AGPL-3.0-only"}

def parse_map_file(map_path):
    """Видобути список усіх об'єктних файлів, реально злінкованих у фінальний образ"""
    used_objects = set()
    map_text = Path(map_path).read_text(encoding="utf-8", errors="ignore")
    
    # Шукаємо секції розподілу коду (.text, .rodata, .data)
    object_regex = re.compile(r'([\w\/\.\-]+\.(?:o|a))(?:\([\w\.\-]+\))?')
    for match in object_regex.finditer(map_text):
        used_objects.add(match.group(1))
    return used_objects

def analyze_components(used_objects):
    """Зіставити об'єкти з базою компонентів та виявити активні ліцензії"""
    detected_components = {}
    
    for obj in used_objects:
        obj_str = str(obj)
        matched = False
        for comp_id, info in COMPONENT_DATABASE.items():
            if re.search(info["pattern"], obj_str, re.IGNORECASE):
                if comp_id not in detected_components:
                    detected_components[comp_id] = {
                        "info": info,
                        "matched_objects": []
                    }
                detected_components[comp_id]["matched_objects"].append(obj_str)
                matched = True
                break
    return detected_components

def generate_cyclonedx_sbom(detected, output_path, binary_hash):
    """Згенерувати машинночитний SBOM у форматі CycloneDX 1.5 JSON"""
    sbom = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "version": 1,
        "metadata": {
            "component": {
                "name": "FlightController-MainFirmware",
                "version": "3.2.0-release",
                "type": "firmware",
                "hashes": [{"alg": "SHA-256", "content": binary_hash}]
            }
        },
        "components": []
    }
    
    for comp_id, data in detected.items():
        info = data["info"]
        comp_entry = {
            "type": "library",
            "name": info["name"],
            "version": info["version"],
            "purl": info["purl"],
            "supplier": {"name": info["supplier"]},
            "licenses": [{"license": {"id": info["license_spdx"]}}],
            "properties": [
                {"name": "embedded:linked_objects_count", "value": str(len(data["matched_objects"]))}
            ]
        }
        sbom["components"].append(comp_entry)
        
    Path(output_path).write_text(json.dumps(sbom, indent=2, ensure_ascii=False), encoding="utf-8")

def generate_notice_file(detected, output_path):
    """Згенерувати зведений файл THIRD_PARTY_LICENSES.txt для інструкції користувача"""
    lines = [
        "================================================================================",
        "ВІДОМОСТІ ПРО ЛІЦЕНЗІЇ СТОРОННЬОГО ПРОГРАМНОГО ЗАБЕЗПЕЧЕННЯ",
        "Цей виріб містить програмні компоненти з відкритим вихідним кодом.",
        "================================================================================\n"
    ]
    for comp_id, data in detected.items():
        info = data["info"]
        lines.append(f"Компонент : {info['name']}")
        lines.append(f"Версія    : {info['version']}")
        lines.append(f"Ліцензія  : {info['license_spdx']}")
        lines.append(f"Автор     : {info['supplier']}")
        lines.append(f"Модулів   : {len(data['matched_objects'])} об'єктів злінковано")
        lines.append("-" * 80 + "\n")
        
    Path(output_path).write_text("\n".join(lines), encoding="utf-8")

def main():
    if len(sys.argv) < 3:
        print("Використання: python firmware_sbom_scanner.py <firmware.map> <firmware.bin>")
        sys.exit(1)
        
    map_file = sys.argv[1]
    bin_file = sys.argv[2]
    
    bin_hash = hashlib.sha256(Path(bin_file).read_bytes()).hexdigest()
    linked_objs = parse_map_file(map_file)
    detected = analyze_components(linked_objs)
    
    # Перевірка на заборонені копілефтні ліцензії (CI Gate)
    violations = []
    for comp_id, data in detected.items():
        lic = data["info"]["license_spdx"]
        if lic in BANNED_LICENSES:
            violations.append(f"Компонент '{data['info']['name']}' має копілефтну ліцензію {lic}")
            
    if violations:
        print("\n[ПОМИЛКА ЛІЦЕНЗІЙНОГО ШЛЮЗУ] Знайдено несумісні ліцензії:")
        for v in violations:
            print(f"  ❌ {v}")
        sys.exit(2)
        
    out_sbom = Path(bin_file).with_suffix(".cdx.json")
    out_notice = Path(bin_file).parent / "THIRD_PARTY_LICENSES.txt"
    
    generate_cyclonedx_sbom(detected, out_sbom, bin_hash)
    generate_notice_file(detected, out_notice)
    print(f"\n[УСПІХ] Знайдено компонентів: {len(detected)}. Згенеровано SBOM: {out_sbom}")

if __name__ == "__main__":
    main()
