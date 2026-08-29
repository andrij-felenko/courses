# -*- coding: utf-8 -*-
"""Константи випуску, апаратна матриця й примітиви звітування.

Тут навмисно немає читання конфігів: матриця ревізій — частина коду релізу,
тож будь-яка її зміна проходить через рев'ю й лишається в історії git.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import NoReturn

# Відбитки відкритих ключів GPG інженерів релізу. Підпис тегу приймається
# лише від когось із цього списку — «просто дійсний підпис» замало.
AUTHORIZED_RELEASE_KEY_FINGERPRINTS = {
    "9E8B7A6C5D4E3F2A1B0C9D8E7F6A5B4C3D2E1F0A",
    "1A2B3C4D5E6F7A8B9C0D1E2F3A4B5C6D7E8F9A0B",
}

# Апаратна матриця: пресет CMake, каталог збірки (мусить збігатися з binaryDir
# пресета), ліміт слота застосунку у Flash і бітова маска сумісності.
HARDWARE_TARGETS = {
    "revB": {
        "mcu": "STM32G474RE",
        "preset": "prod-revB",
        "build_dir": "build/prod-revB",
        "flash_limit": 262144,   # 256 КіБ під слот застосунку
        "hw_mask": 0x0002,
    },
    "revC": {
        "mcu": "STM32G484RE",
        "preset": "prod-revC",
        "build_dir": "build/prod-revC",
        "flash_limit": 524288,   # 512 КіБ
        "hw_mask": 0x0004,
    },
}

PRODUCT_ID = "iot-sensor-node"
SIGNING_KEY_ID = "prod-firmware-signer-v1"

# Формат заголовка Secure Boot. Ті самі числа зашиті в завантажувачі
# (див. c/image_header.h) — розійдуться вони, і пристрій відкине образ.
SECURE_BOOT_MAGIC = 0x53424F54  # "SBOT"
HEADER_SIZE = 128
SIGNED_PREFIX_LEN = 52          # байти заголовка, що входять у підпис
DIGEST_LEN = 32
SIGNATURE_LEN = 64

# Лічильник anti-rollback. Піднімається руками, коли закрито вразливість:
# пристрій відмовиться відкотитися на образ із меншим значенням.
SECURITY_COUNTER = 3

# Склад прошивки для SBOM. У великому дереві це читається з lock-файла
# менеджера залежностей; тут залежності зафіксовані підмодулями git.
DEPENDENCIES = (
    ("FreeRTOS-Kernel", "10.5.1", "pkg:github/FreeRTOS/FreeRTOS-Kernel@V10.5.1"),
    ("mbedTLS", "3.4.0", "pkg:github/Mbed-TLS/mbedtls@v3.4.0"),
    ("STM32G4-HAL", "1.5.0", "pkg:github/STMicroelectronics/STM32CubeG4@v1.5.0"),
)


class ReleaseError(RuntimeError):
    """Провал воріт. Ловиться лише в main() — саме там прибирають сміття."""

    def __init__(self, stage: str, msg: str) -> None:
        super().__init__(f"[{stage}] {msg}")
        self.stage = stage
        self.msg = msg


def log(stage: str, msg: str) -> None:
    stamp = datetime.now(timezone.utc).strftime("%H:%M:%S")
    # flush обов'язковий: у логах CI stdout буферизований поблоково,
    # і без нього рядки лягають не в тому порядку, що stderr.
    print(f"[{stamp}] [{stage}] {msg}", flush=True)


def fail(stage: str, msg: str) -> NoReturn:
    raise ReleaseError(stage, msg)
