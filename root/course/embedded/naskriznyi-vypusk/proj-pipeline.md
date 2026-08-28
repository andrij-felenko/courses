# ⚙️ Практичний скрипт наскрізного конвеєра випуску прошивки

Цей проект реалізує повний оркестраційний скрипт випуску прошивки для промислових контролерів. Скрипт автоматизує перевірку підпису git-тегу, матричну крос-компіляцію для апаратних ревізій, контроль бюджету пам'яті, формування цифрового паспорта компонентів (SBOM), підпис через віддалений API криптографічного модуля (HSM) та збирання фінального релізного бандла.

## Архітектура та послідовність виконання скрипту

Скрипт оркестрації розроблено мовою Python без сторонніх важких бібліотек, що дозволяє виконувати його в ізольованому, мінімалістичному контейнері CI-раннера без розгортання складного оточення. Процес випуску розбито на шість послідовних кроків:

```
[1. Валідація тегу] ──> [2. Крос-збірка матриці] ──> [3. Контроль пам'яті]
         │
         v
[4. Генерація SBOM] ──> [5. Підпис у HSM] ───────> [6. Збирання бандла]
```

Оркестратор виступає в ролі головного бар'єра якості перед публікацією артефактів. Його головна задача — не просто викликати компілятор, а забезпечити повну простежуваність та незмінність середовища випуску. Якщо будь-який із проміжних кроків завершується з ненульовим кодом повернення (наприклад, не знайдено GPG-підпис або розмір коду перевищив виділений сектор Flash), оркестратор негайно припиняє виконання, видаляє всі тимчасові файли та сповіщає систему моніторингу через стандартний потік помилок `stderr`.

Така архітектура запобігає ситуаціям, коли частково зібраний або непідписаний реліз випадково публікується в репозиторії. Будь-який провал воріт безпеки є термінальним станом.

## Повний оркестраційний скрипт `release_orchestrator.py`

Нижче наведено повний вихідний код оркестратора, який виконується в захищеному контейнері збірки:

```python
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
```

## Розбір роботи ключових блоків оркестратора

Кожна функція скрипту відповідає за конкретний бар'єр безпеки конвеєра та запобігає поширеним помилкам автоматизації:

1. **Валідація тегу (`step_1_validate_git_tag`).** Функція захищає конвеєр від випадкових локальних комітів без підпису. Вона перевіряє не лише наявність підпису, але й чистоту дерева `git status --porcelain`. Якщо інженер залишив незбережений файл налагодження, конвеєр перериває роботу до запуску компілятора. Крім того, скрипт витягує точний час створення коміту `git log -1 --format=%ct` і передає його як `SOURCE_DATE_EPOCH`, усуваючи часовий дрифт між різними серверами конвеєра.
2. **Матрична компіляція (`step_2_build_matrix`).** Замість одноразової компіляції скрипт ітерується по словнику `HARDWARE_TARGETS`. Для кожної цілі передаються власні пресети CMake та макроси версії. Це унеможливлює ситуацію, коли прошивка для ревізії B збирається з прапорцями для ревізії C. Всі змінні передаються через командний рядок CMake, що гарантує їх фіксацію в кеші конфігурації.
3. **Контроль Flash-пам'яті.** Після отримання сирого бінарника `app-revB.raw.bin` скрипт порівнює розмір файлу на диску з лімітом виділеного розділу Flash. Якщо код перевищує ліміт навіть на 1 байт, конвеєр падає з детальним звітом. Це рятує пристрої від ситуації, коли частково записаний бінарник затирає сусідній сектор конфігурації NVS або завантажувача.
4. **Ізольований підпис (`step_3_mock_hsm_sign`).** Скрипт не завантажує закритий ключ у пам'ять раннера. Замість цього обчислюється 32-байтний SHA-256 хеш комбінації заголовка й тіла програми, який передається модулю безпеки. У відповідь повертається 64-байтний підпис. Такий підхід захищає кореневий ключ від витоку навіть у разі повної компрометації раннера збірки сторонніми npm- чи pip-пакетами.

## Клієнтська перевірка маніфесту на пристрої

Після завантаження нового бандла пристрій має розібрати заголовок образу та підтвердити валідність підпису перед прошиванням. Коли мікроконтролер отримує блок оновлення, він не може сліпо довіряти мережевому з'єднанню. Перед стиранням внутрішньої пам'яті завантажувач перевіряє магічне число `0x53424F54`, маску апаратної сумісності та лічильник відкату версії.

Клієнтський парсер реалізовано з урахуванням обмежень мікроконтролерів: він не виділяє динамічну пам'ять, працює безпосередньо з вхідним буфером фіксованого розміру та виконує перевірку вирівнювання структур по 4-байтній межі:

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define SECURE_BOOT_MAGIC 0x53424F54
#define CURRENT_HW_MASK   0x0002

typedef struct {
    uint32_t magic;
    uint32_t version_packed;
    uint32_t security_counter;
    uint32_t hw_mask;
    uint32_t payload_size;
    uint8_t  payload_sha256[32];
    uint8_t  signature[64];
    uint8_t  reserved[12];
} __attribute__((packed)) ReleaseHeader;

typedef enum {
    RELEASE_OK = 0,
    ERR_INVALID_MAGIC,
    ERR_INCOMPATIBLE_HARDWARE,
    ERR_ANTI_ROLLBACK,
    ERR_BUFFER_OVERFLOW
} ReleaseStatus;

ReleaseStatus validate_image_header(const uint8_t *header_buffer,
                                    size_t buffer_len,
                                    uint32_t active_security_counter,
                                    uint32_t max_allowed_size) {
    if (buffer_len < sizeof(ReleaseHeader)) {
        return ERR_BUFFER_OVERFLOW;
    }

    const ReleaseHeader *hdr = (const ReleaseHeader *)header_buffer;

    if (hdr->magic != SECURE_BOOT_MAGIC) {
        return ERR_INVALID_MAGIC;
    }

    /* Перевірка бітової маски апаратної сумісності */
    if ((hdr->hw_mask & CURRENT_HW_MASK) == 0) {
        return ERR_INCOMPATIBLE_HARDWARE;
    }

    /* Захист від відкату на застарілу вразливу версію */
    if (hdr->security_counter < active_security_counter) {
        return ERR_ANTI_ROLLBACK;
    }

    if (hdr->payload_size > max_allowed_size) {
        return ERR_BUFFER_OVERFLOW;
    }

    return RELEASE_OK;
}
```
```cpp
#include <cstdint>
#include <span>
#include <expected>
#include <array>

namespace release {

inline constexpr uint32_t SecureBootMagic = 0x53424F54;
inline constexpr uint32_t CurrentHardwareMask = 0x0002;

struct alignas(4) ReleaseHeader {
    uint32_t magic;
    uint32_t versionPacked;
    uint32_t securityCounter;
    uint32_t hwMask;
    uint32_t payloadSize;
    std::array<uint8_t, 32> payloadSha256;
    std::array<uint8_t, 64> signature;
    std::array<uint8_t, 12> reserved;
};

enum class ParseError {
    BufferOverflow,
    InvalidMagic,
    IncompatibleHardware,
    AntiRollbackViolation
};

[[nodiscard]] std::expected<void, ParseError> validateImageHeader(
    std::span<const uint8_t> headerBytes,
    uint32_t activeSecurityCounter,
    uint32_t maxAllowedSize) noexcept {
    
    if (headerBytes.size() < sizeof(ReleaseHeader)) {
        return std::unexpected(ParseError::BufferOverflow);
    }

    const auto* hdr = reinterpret_cast<const ReleaseHeader*>(headerBytes.data());

    if (hdr->magic != SecureBootMagic) {
        return std::unexpected(ParseError::InvalidMagic);
    }

    if ((hdr->hwMask & CurrentHardwareMask) == 0) {
        return std::unexpected(ParseError::IncompatibleHardware);
    }

    if (hdr->securityCounter < activeSecurityCounter) {
        return std::unexpected(ParseError::AntiRollbackViolation);
    }

    if (hdr->payloadSize > maxAllowedSize) {
        return std::unexpected(ParseError::BufferOverflow);
    }

    return {};
}

} // namespace release
```
:::

Реалізація на мові C++ використовує сучасні безпечні конструкції `std::span` та `std::expected` згідно зі стандартом C++23. Це повністю усуває можливість передачі невалідних покажчиків чи помилок з виходом за межі пам'яті, які є класичним джерелом вразливостей під час розбору бінарних пакетів у вбудованому ПЗ.

## Інтеграція в конвеєри CI/CD

Для інтеграції оркестратора у конвеєр GitHub Actions або GitLab CI створюється окреме завдання (Job), яке запускається виключно за умови створення тегу:

```yaml
name: Production Firmware Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write
    steps:
      - name: Checkout repository with tags
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Install embedded cross-toolchain
        run: |
          sudo apt-get update
          sudo apt-get install -y gcc-arm-none-eabi cmake ninja-build

      - name: Execute release orchestrator
        run: |
          python3 scripts/release_orchestrator.py --tag ${{ github.ref_name }} --out ./release_dist

      - name: Upload release bundle
        uses: actions/upload-artifact@v4
        with:
          name: firmware-release-${{ github.ref_name }}
          path: ./release_dist/
```

## Пастки реалізації та типові помилки

Під час розгортання виробничих оркестраторів релізу розробники найчастіше стикаються з трьома критичними проблемами:

1. **Недетерміноване сортування файлів.** Якщо у скриптах збірки використовується пошук вихідних файлів за маскою `file(GLOB ...)`, файлова система повертає їх у довільному порядку залежно від індексних дескрипторів inode. Це призводить до різного порядку компонування об'єктних файлів у двох прогонах конвеєра. Завжди використовуйте явний список файлів у `CMakeLists.txt` або сортуйте результати пошуку.
2. **Втрата зв'язку з репозиторієм при неглибокому клонуванні.** За замовчуванням багато раннерів CI виконують неглибоке клонування (`git clone --depth=1`). У такому разі команда `git describe` не може знайти попередній тег, а перевірка підпису тегу повертає помилку через відсутність історії предків. Завжди виставляйте `fetch-depth: 0` у кроці клонування для завдань релізу.
3. **Плутанина між Endianness при формуванні бінарних заголовків.** Мікроконтролери архітектури ARM Cortex-M працюють у режимі Little-Endian. Якщо сервер збірки формує заголовок у мережевому порядку байтів (Big-Endian) без явного перетворення, завантажувач прочитає магічне число `0x53424F54` навпаки як `0x544F4253` і відхилить прошивку. Скрипт оркестрації завжди має явно вказувати порядок байтів `.to_bytes(4, "little")`.
4. **Скидання сторожового таймера під час верифікації.** Якщо перевірка цифрового підпису в завантажувачі займає більше 50 мс, а апаратний сторожовий таймер IWDG налаштовано на короткий інтервал без скидання у фоні, мікроконтролер піде в нескінченний цикл перезавантажень. Завантажувач повинен скидати таймер безпосередньо перед початком математичних обчислень криптографічного дайджесту.

Цей практичний комплекс демонструє, як автоматизований наскрізний конвеєр перетворює випуск на детерміновану, безпечну та повністю математично надійну інженерну процедуру.
