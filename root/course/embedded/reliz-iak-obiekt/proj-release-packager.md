# Практикум: утиліта збирання релізного пакета та верифікатор завантажувача

Створення надійного релізу вбудованої системи вимагає двох взаємодоповнюючих інженерних компонентів: хостової утиліти автоматизованого збирання пакета (англ. *Release Packager*), яка працює на сервері неперервної інтеграції, та вбудованого модуля верифікації (англ. *Bootloader Verifier*), що виконується на цільовому мікроконтролері перед записом або запуском нової програми.

## Архітектура пакувальника релізу

Хостова утиліта пакування вирішує критичне завдання: перетворити «сирий» двійковий файл компіляції (`.bin`) на неподільну криптографічну капсулу. Цей процес не зводиться до звичайного склеювання файлів. Пакувальник зобов'язаний суворо дотримуватися послідовності кроків:

1. **Валідація вхідного образу:** перевірка, що файл `.bin` не порожній, містить валідний вектор початкового стека (MSP в межах адрес внутрішньої RAM) та точку скидання (Reset Handler у межах адрес Flash-пам'яті цільового процесора).
2. **Обчислення цілісності:** генерація криптографічного дайджесту SHA-256 над точним розміром корисного навантаження.
3. **Формування структури дескриптора:** упаковка полів маніфесту (магічне число, апаратний ID, межі ревізій PCB, SemVer, індекс захисту від відкату, адреса Flash, розмір та геш) у 64 байти двійкового формату з суворим дотриманням порядку байтів *little-endian*.
4. **Накладання цифрового підпису:** взаємодія з криптографічним ключем Ed25519 для генерації 64-байтного цифрового підпису над сформованими 64 байтами метаданих. У промислових середовищах закритий ключ не зберігається у файловій системі сервера, а знаходиться в апаратному модулі безпеки (HSM) або хмарному сервісі управління ключами (KMS), куди пакувальник передає 64 байти дескриптора через стандартний інтерфейс PKCS#11.
5. **Складання релізної капсули:** створення результуючого файлу `.fwpkg`, який складається зі 128-байтного дескриптора (метадані + підпис) та тіла корисного навантаження.

### Хостовий пакувальник на Python

Нижче наведено повний автономний скрипт формування підписаного релізного пакета.

```python
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
```

## Модуль верифікації для первинного завантажувача

На стороні мікроконтролера завантажувач реалізує строгий покроковий автомат перевірки. Пам'ять мікроконтролера обмежена, тому завантажувач не копіює весь образ у RAM. Він зчитує лише перші 128 байтів у стек або локальний буфер, проводить перевірки сумісності та підпису, і лише після позитивного вердикту починає потоковий запис корисного навантаження у Flash-пам'ять із паралельним обчисленням SHA-256.

Розгляньмо реалізацію модуля верифікації мовами C та сучасним C++.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

/* Спрощений інтерфейс криптобібліотеки (mbedTLS / Monocypher) */
typedef struct {
    uint32_t magic_word;
    uint32_t header_version;
    uint32_t target_hw_id;
    uint8_t  hw_rev_min;
    uint8_t  hw_rev_max;
    uint16_t flags;
    uint8_t  ver_major;
    uint8_t  ver_minor;
    uint8_t  ver_patch;
    uint8_t  ver_pre_flags;
    uint32_t security_version;
    uint32_t payload_size;
    uint32_t load_address;
    uint8_t  payload_sha256[32];
    uint8_t  signature[64];
} __attribute__((packed)) firmware_header_t;

typedef enum {
    VERIFY_OK = 0,
    VERIFY_ERR_MAGIC = 1,
    VERIFY_ERR_HW_MISMATCH = 2,
    VERIFY_ERR_ROLLBACK = 3,
    VERIFY_ERR_SIGNATURE = 4,
    VERIFY_ERR_HASH = 5
} verify_status_t;

/* Зовнішні апаратні функції платформи */
extern uint32_t bsp_get_hardware_id(void);
extern uint8_t  bsp_get_board_revision(void);
extern uint32_t bsp_get_otp_security_version(void);
extern const uint8_t* bsp_get_root_public_key(void);
extern int crypto_ed25519_verify(const uint8_t sig[64], const uint8_t *msg, size_t len, const uint8_t pubkey[32]);
extern void crypto_sha256_stream(const uint8_t *data, size_t len, uint8_t out_digest[32]);

verify_status_t bootloader_verify_image(const firmware_header_t *hdr, const uint8_t *payload) {
    /* 1. Перевірка магічного числа */
    if (hdr->magic_word != 0x46574D46U || hdr->header_version != 1U) {
        return VERIFY_ERR_MAGIC;
    }

    /* 2. Перевірка сумісності із залізом */
    if (hdr->target_hw_id != bsp_get_hardware_id()) {
        return VERIFY_ERR_HW_MISMATCH;
    }
    uint8_t current_rev = bsp_get_board_revision();
    if (current_rev < hdr->hw_rev_min || current_rev > hdr->hw_rev_max) {
        return VERIFY_ERR_HW_MISMATCH;
    }

    /* 3. Перевірка на атаку відкату (Anti-rollback) */
    if (hdr->security_version < bsp_get_otp_security_version()) {
        return VERIFY_ERR_ROLLBACK;
    }

    /* 4. Верифікація криптографічного підпису заголовка */
    const uint8_t *pubkey = bsp_get_root_public_key();
    if (crypto_ed25519_verify(hdr->signature, (const uint8_t*)hdr, 64, pubkey) != 0) {
        return VERIFY_ERR_SIGNATURE;
    }

    /* 5. Потокова перевірка цілісності корисного коду */
    uint8_t calculated_hash[32];
    crypto_sha256_stream(payload, hdr->payload_size, calculated_hash);
    if (memcmp(calculated_hash, hdr->payload_sha256, 32) != 0) {
        return VERIFY_ERR_HASH;
    }

    return VERIFY_OK;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <expected>
#include <algorithm>

enum class VerifyError : std::uint8_t {
    MagicMismatch = 1,
    HardwareMismatch,
    RollbackDetected,
    InvalidSignature,
    PayloadHashMismatch
};

#pragma pack(push, 1)
struct FirmwareHeader {
    std::uint32_t magic_word;
    std::uint32_t header_version;
    std::uint32_t target_hw_id;
    std::uint8_t  hw_rev_min;
    std::uint8_t  hw_rev_max;
    std::uint16_t flags;
    std::uint8_t  ver_major;
    std::uint8_t  ver_minor;
    std::uint8_t  ver_patch;
    std::uint8_t  ver_pre_flags;
    std::uint32_t security_version;
    std::uint32_t payload_size;
    std::uint32_t load_address;
    std::array<std::uint8_t, 32> payload_sha256;
    std::array<std::uint8_t, 64> signature;

    [[nodiscard]] constexpr std::span<const std::uint8_t, 64> signed_region() const noexcept {
        return std::span<const std::uint8_t, 64>(reinterpret_cast<const std::uint8_t*>(this), 64);
    }
};
#pragma pack(pop)

class HardwarePlatform {
public:
    [[nodiscard]] static std::uint32_t hardware_id() noexcept;
    [[nodiscard]] static std::uint8_t board_revision() noexcept;
    [[nodiscard]] static std::uint32_t security_version() noexcept;
    [[nodiscard]] static std::span<const std::uint8_t, 32> root_public_key() noexcept;
};

class CryptoEngine {
public:
    [[nodiscard]] static bool verify_ed25519(
        std::span<const std::uint8_t, 64> signature,
        std::span<const std::uint8_t> message,
        std::span<const std::uint8_t, 32> public_key) noexcept;

    [[nodiscard]] static std::array<std::uint8_t, 32> calculate_sha256(
        std::span<const std::uint8_t> data) noexcept;
};

class ImageVerifier {
public:
    [[nodiscard]] static std::expected<void, VerifyError> verify(
        const FirmwareHeader& header,
        std::span<const std::uint8_t> payload) noexcept {
        
        // 1. Перевірка валідності сигнатури структури
        if (header.magic_word != 0x46574D46U || header.header_version != 1U) {
            return std::unexpected(VerifyError::MagicMismatch);
        }

        // 2. Відповідність цільової апаратної платформи
        if (header.target_hw_id != HardwarePlatform::hardware_id()) {
            return std::unexpected(VerifyError::HardwareMismatch);
        }
        const auto rev = HardwarePlatform::board_revision();
        if (rev < header.hw_rev_min || rev > header.hw_rev_max) {
            return std::unexpected(VerifyError::HardwareMismatch);
        }

        // 3. Контроль відкату версії безпеки
        if (header.security_version < HardwarePlatform::security_version()) {
            return std::unexpected(VerifyError::RollbackDetected);
        }

        // 4. Перевірка підпису заголовка
        const bool sig_valid = CryptoEngine::verify_ed25519(
            header.signature,
            header.signed_region(),
            HardwarePlatform::root_public_key()
        );
        if (!sig_valid) {
            return std::unexpected(VerifyError::InvalidSignature);
        }

        // 5. Цілісність образу
        if (payload.size() != header.payload_size) {
            return std::unexpected(VerifyError::PayloadHashMismatch);
        }
        const auto actual_hash = CryptoEngine::calculate_sha256(payload);
        if (actual_hash != header.payload_sha256) {
            return std::unexpected(VerifyError::PayloadHashMismatch);
        }

        return {};
    }
};
```
:::

## Інтеграція в конвеєр CI/CD та апаратне тестування

У промислових проєктах утиліта збирання релізу не запускається розробниками вручну на персональних комп'ютерах. Вона інтегрується в захищений конвеєр неперервної інтеграції (наприклад, GitHub Actions або GitLab CI Runner), де доступ до закритого ключа строго ізольовано.

Типовий крок конвеєра виконує автоматизовану послідовність:

```bash
# Приклад кроку підписання в релізному конвеєрі CI
- name: Package and Sign Firmware Release
  env:
    SIGNING_KEY_SECRET: ${{ secrets.PROD_RELEASE_ED25519_KEY }}
  run: |
    echo "$SIGNING_KEY_SECRET" > /tmp/release_key.priv
    python3 scripts/firmware_packager.py \
      --payload build/firmware.bin \
      --key /tmp/release_key.priv \
      --out dist/sensor_v1.4.0.fwpkg \
      --hw-id 0x0000A1F0 \
      --rev-min 1 \
      --rev-max 3 \
      --ver 1.4.0 \
      --sec-ver 4 \
      --load-addr 0x08020000
    rm -f /tmp/release_key.priv
```

Після генерації файлу `.fwpkg` конвеєр запускає автоматизоване HIL-тестування (англ. *Hardware-in-the-Loop*). Спеціальний раннер прошиває релізний пакет у фізичний мікроконтролер на випробувальному стенді через тестовий завантажувач, перевіряє коректність відповіді модуля верифікації, фіксує відсутність апаратних відмов `HardFault` і тільки після цього публікує артефакт на сервері дистрибуції.

## Практичні інженерні тонкощі та підводні камені

Реалізація пакування та верифікації у реальних виробах вимагає врахування низки апаратних обмежень:

1. **Вирівнювання пам'яті під час запису у Flash.** Більшість сучасних мікроконтролерів (зокрема лінійки STM32H7, STM32G4 та ESP32-S3) мають внутрішні контролери Flash із фіксованим розміром слова запису: 16 байтів (128 біт) або 32 байти (256 біт). Якщо розмір скомпільованого бінарника не кратний розміру слова запису, спроба прямого запису кінцевого фрагмента викличе апаратну помилку шини `BusFault` або запис некоректних даних. Пакувальник зобов'язаний або доповнити образ нульовими байтами (padding) до кратності слова, або точно зберегти `payload_size`, щоб завантажувач сформував вирівняний фінальний блок.
2. **Потокове обчислення гешу (Zero-Copy Streaming).** Якщо пристрій має 32 КБ RAM, а оновлення займає 512 КБ, образ неможливо прийняти повністю в пам'ять перед верифікацією. Завантажувач використовує потоковий інтерфейс: ініціалізує контекст `sha256_init()`, приймає фрагменти по 512–1024 байти через UART або радіоканал, оновлює стан гешу через `sha256_update()` і одночасно записує блок у буферний слот Flash. Фіналізація `sha256_final()` виконується після завершення прийому останнього пакета.
3. **Захист від атак за часом виконання (Timing Attacks).** Порівняння відбитків або відкритих ключів не повинно перериватися на першому незбіжному байті через стандартну функцію `memcmp()`. Зловмисник, вимірюючи час відповіді завантажувача з точністю до мікросекунд через осцилограф або логічний аналізатор, може побайтово підбирати правильні значення. Для порівняння криптографічних блоків завжди використовується функція з постійним часом виконання `crypto_memcmp_const_time()`.
4. **Атомарність оновлення eFuse.** Пропалювання комірки лічильника безпеки (Security Version) є незворотною операцією. Якщо живлення зникне посеред процесу подачі підвищеної напруги програмування на eFuse-комірку, біт може залишитися в невизначеному напівпровідному стані. Тому операція запису eFuse виконується строго **після** того, як нова прошивка записана у пам'ять і підтвердила свою цілісність, але **до** першої передачі керування на її точку входу.
