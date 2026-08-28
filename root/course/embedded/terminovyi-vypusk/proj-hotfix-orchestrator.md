# ⚙️ Оркестратор екстреного випуску: валідація диффу, збірка та контроль відкату

<preknowlist>
- [Наскрізний випуск](root:embedded/naskriznyi-vypusk) — базовий конвеєр збірки, матриця конфігурацій та підпис артефактів.
- [CI для прошивки](root:embedded/firmware-ci) — автоматичне тестування та інтеграція вбудованих систем.
- [Захист від відкату](root:sf-security/replay-protection) — концепція асиметричного підпису та блокування старих образів через монотонні лічильники.
</preknowlist>

Екстрений випуск виправлення (hotfix) не пробачає людських помилок під час ручного втручання. Коли інженер у стані стресу під час нічного інциденту намагається власноруч підготувати релізний бінарник, імовірність випадкової помилки зростає у десятки разів. Достатньо випадково підтягнути у виправлення незафіксовані зміни з головної гілки розробки, пропустити інкремент версії в конфігурації або забути підняти монотонний лічильник безпеки в заголовку образу — і наслідки стануть катастрофічними: від масового блокування завантажувачів (bricked devices) до відкриття лазівки для атак типу «відкат версії» (downgrade attack).

Цей проєкт реалізує комплексну автоматизовану систему оркестрації та валідації екстреного випуску, яка гарантує безпомилковість процесу за рахунок суворого контролю на двох рівнях:
1. **Інструмент статичної інспекції диффу (`hotfix_diff_inspector.py`):** скрипт на стороні сервера автоматизації CI/CD, який перевіряє, що гілка hotfix відгалужена суворо від підтвердженого релізного тегу, обсяг змін не перевищує встановленого бюджету безпеки (diff budget), а заголовок версії містить коректні семантичні константи та оновлений лічильник захисту від відкату.
2. **Вбудований модуль верифікації образу у мікроконтролері (`emergency_validator`):** модуль на стороні вбудованого завантажувача (Bootloader), який виконує парсинг бінарного заголовка, звіряє монотонний лічильник з апаратним регістром eFuse, перевіряє хеш SHA-256 і керує переходом системи у режим пробного запуску (trial boot) з можливістю автоматичного повернення у резервний банк пам'яті.

## 1. Скрипт перевірки чистоти екстреного диффу

Скрипт інспекції диффу запускається на найпершому кроці екстреного конвеєра збірки, до запуску компіляторів. Його завдання — унеможливити потрапляння в реліз випадкових правок, які не стосуються закриття конкретної вразливості або дефекту.

Скрипт виконує три послідовні перевірки:
1. **Перевірка предка гілки (`merge-base check`):** обчислює спільний предок між поточною гілкою та базовим релізним тегом. Якщо спільний предок не збігається з комітом тегу, це означає, що гілку було створено від `main` або іншої проміжної гілки. У такому разі конвеєр негайно обривається.
2. **Аудит змінених файлів (`forbidden paths check`):** перевіряє список модифікованих файлів за регулярними виразами. Зміна скриптів компонувальника (`*.ld`), файлів апаратної ініціалізації периферії HAL, каталогів сторонніх бібліотек (`third_party/`) або глобальних конфігурацій CMake суворо заборонена у межах hotfix.
3. **Бюджет доданих/видалених рядків (`diff budget check`):** аналізує сумарний обсяг змін. Для екстреного випуску встановлюється жорсткий ліміт (за замовчуванням — не більше 150 рядків коду у сумі та не більше 4 файлів).

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""hotfix_diff_inspector.py — Автоматичний аудит чистоти та меж екстреного патчу."""

import sys
import os
import subprocess
import re

MAX_ALLOWED_CHANGED_LINES = 150
MAX_ALLOWED_CHANGED_FILES = 4

FORBIDDEN_PATH_PATTERNS = [
    r"^third_party/",
    r"^drivers/hal/",
    r"^linker/.*\.ld$",
    r"^cmake/toolchain-.*\.cmake$",
    r"^\.github/workflows/"
]

def run_git_command(args):
    """Виконання команди Git із перевіркою результату."""
    result = subprocess.run(["git"] + args, capture_output=True, text=True, check=True)
    return result.stdout.strip()

def validate_hotfix_branch(base_tag, hotfix_branch):
    """Повна валідація меж та чистоти екстреної гілки."""
    print(f"[*] Перевірка походження гілки: {hotfix_branch} від тегу {base_tag}")
    
    # 1. Перевірка, що base_tag є прямим предком гілки hotfix
    merge_base = run_git_command(["merge-base", base_tag, hotfix_branch])
    tag_commit = run_git_command(["rev-parse", f"{base_tag}^{{commit}}"])
    
    if merge_base != tag_commit:
        print(f"[!] ПОМИЛКА: Гілка {hotfix_branch} відгалужена НЕ від релізного тегу {base_tag}!")
        print(f"    Merge base: {merge_base}, Tag commit: {tag_commit}")
        sys.exit(1)
        
    print("[+] Базовий тег підтверджено. Аналіз змінених файлів...")
    
    # 2. Отримання списку змінених файлів
    diff_files = run_git_command(["diff", "--name-only", base_tag, hotfix_branch]).splitlines()
    diff_files = [f for f in diff_files if f.strip()]
    
    if len(diff_files) > MAX_ALLOWED_CHANGED_FILES:
        print(f"[!] ПОМИЛКА: Кількість змінених файлів ({len(diff_files)}) перевищує ліміт {MAX_ALLOWED_CHANGED_FILES}!")
        sys.exit(1)
        
    for file_path in diff_files:
        for pattern in FORBIDDEN_PATH_PATTERNS:
            if re.search(pattern, file_path):
                print(f"[!] ПОМИЛКА: Зміна критичного системного шляху заборонена в hotfix: {file_path}")
                sys.exit(1)
                
    # 3. Підрахунок кількості доданих/видалених рядків
    diff_stat = run_git_command(["diff", "--shortstat", base_tag, hotfix_branch])
    match = re.search(r"(\d+)\s+insertions?\(\+\),\s+(\d+)\s+deletions?\(-\)", diff_stat)
    if match:
        ins, dels = int(match.group(1)), int(match.group(2))
        total_changed = ins + dels
        if total_changed > MAX_ALLOWED_CHANGED_LINES:
            print(f"[!] ПОМИЛКА: Обсяг змін ({total_changed} рядків) перевищує бюджет hotfix ({MAX_ALLOWED_CHANGED_LINES})!")
            sys.exit(1)
            
    print(f"[+] Дифф чистий: {len(diff_files)} файлів, {diff_stat}. Перевірка пройдена успішно.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Використання: python hotfix_diff_inspector.py <base_tag> <hotfix_branch>")
        sys.exit(1)
    validate_hotfix_branch(sys.argv[1], sys.argv[2])
```

## 2. Модуль верифікації образу у мікроконтролері

На стороні мікроконтролера модуль верифікації інтегрується у структуру безпечного завантажувача (Secure Bootloader) або у фонову службу оновлення. Він працює без використання динамічної пам'яті (`malloc`/`free`), спираючись виключно на фіксовані статичні буфери та апаратні криптографічні прискорювачі (якщо вони наявні в мікроконтролері).

Алгоритм виконує сувору поетапну перевірку:
1. Перевірка цілісності магічного числа та розміру заголовка;
2. Звірка ідентифікатора апаратної платформи з регістром Device ID мікроконтролера;
3. Зчитування поточного значення апаратного лічильника безпеки eFuse та перевірка інваріанта `security_counter >= efuse_value`;
4. Обчислення криптографічного хешу SHA-256 по всьому тілу корисного навантаження прошивки;
5. Перевірка цифрового підпису заголовка відкритим ключем виробника, вшитим в одноразово програвану пам'ять (OTP) під час заводського виробництва.

:::tabs
```c
#include "emergency_fw_header.h"
#include <string.h>

/* Апаратні та криптографічні залежності мікроконтролера */
extern uint32_t hw_efuse_read_security_version(void);
extern uint32_t hw_get_platform_id(void);
extern bool crypto_sha256(const uint8_t *data, uint32_t len, uint8_t *out_hash);
extern bool crypto_verify_signature(const uint8_t *pubkey, const uint8_t *hash, const uint8_t *sig);

emergency_validation_status_t emergency_validate_firmware(
    const emergency_fw_header_t *header,
    const uint8_t *payload_data,
    uint32_t payload_len,
    const uint8_t *root_pubkey
) {
    if (!header || !payload_data || !root_pubkey) {
        return EMERGENCY_VAL_ERR_BAD_MAGIC;
    }

    /* 1. Перевірка магічного числа 'EMGY' */
    if (header->magic != EMERGENCY_HEADER_MAGIC) {
        return EMERGENCY_VAL_ERR_BAD_MAGIC;
    }

    /* 2. Перевірка версії структури заголовка */
    if (header->header_version != EMERGENCY_HEADER_VERSION) {
        return EMERGENCY_VAL_ERR_UNSUPPORTED_VERSION;
    }

    /* 3. Звірка ідентифікатора апаратної платформи */
    if (header->target_hw_id != hw_get_platform_id()) {
        return EMERGENCY_VAL_ERR_HW_MISMATCH;
    }

    /* 4. Захист від атак відкату (Anti-Rollback) */
    uint32_t current_efuse_sec = hw_efuse_read_security_version();
    if (header->security_counter < current_efuse_sec) {
        return EMERGENCY_VAL_ERR_ROLLBACK_BLOCKED;
    }

    /* 5. Перевірка розміру корисного навантаження */
    if (header->payload_size != payload_len) {
        return EMERGENCY_VAL_ERR_PAYLOAD_BOUNDS;
    }

    /* 6. Обчислення SHA-256 корисного навантаження */
    uint8_t calculated_sha[EMERGENCY_SHA256_SIZE_BYTES];
    if (!crypto_sha256(payload_data, payload_len, calculated_sha)) {
        return EMERGENCY_VAL_ERR_HASH_MISMATCH;
    }

    if (memcmp(calculated_sha, header->payload_sha256, EMERGENCY_SHA256_SIZE_BYTES) != 0) {
        return EMERGENCY_VAL_ERR_HASH_MISMATCH;
    }

    /* 7. Верифікація цифрового підпису заголовка */
    uint8_t header_hash[EMERGENCY_SHA256_SIZE_BYTES];
    uint32_t signed_header_bytes = sizeof(emergency_fw_header_t) - EMERGENCY_SIG_SIZE_BYTES - sizeof(header->reserved);
    
    if (!crypto_sha256((const uint8_t*)header, signed_header_bytes, header_hash)) {
        return EMERGENCY_VAL_ERR_SIGNATURE_INVALID;
    }

    if (!crypto_verify_signature(root_pubkey, header_hash, header->header_signature)) {
        return EMERGENCY_VAL_ERR_SIGNATURE_INVALID;
    }

    return EMERGENCY_VAL_OK;
}
```
```cpp
#include "emergency_fw_header.hpp"
#include <cstring>
#include <span>
#include <expected>

// Апаратні зовнішні API платформи
extern "C" uint32_t hw_efuse_read_security_version();
extern "C" uint32_t hw_get_platform_id();
extern "C" bool crypto_sha256(const uint8_t* data, uint32_t len, uint8_t* out_hash);
extern "C" bool crypto_verify_signature(const uint8_t* pubkey, const uint8_t* hash, const uint8_t* sig);

namespace emergency {

class FirmwareValidator {
public:
    explicit FirmwareValidator(std::span<const uint8_t> rootPublicKey)
        : rootPublicKey_(rootPublicKey) {}

    [[nodiscard]] std::expected<void, ValidationError> validate(
        const Header& header,
        std::span<const uint8_t> payload
    ) const noexcept {
        // 1. Перевірка магічного числа
        if (header.magic != HeaderMagic) {
            return std::unexpected(ValidationError::BadMagic);
        }

        // 2. Перевірка версії заголовка
        if (header.headerVersion != CurrentHeaderVersion) {
            return std::unexpected(ValidationError::UnsupportedVersion);
        }

        // 3. Звірка ідентифікатора апаратури
        if (header.targetHwId != hw_get_platform_id()) {
            return std::unexpected(ValidationError::HardwareMismatch);
        }

        // 4. Захист від відкату версії безпеки
        const uint32_t activeSecurityVersion = hw_efuse_read_security_version();
        if (header.securityCounter < activeSecurityVersion) {
            return std::unexpected(ValidationError::RollbackBlocked);
        }

        // 5. Перевірка розміру тіла прошивки
        if (header.payloadSize != payload.size()) {
            return std::unexpected(ValidationError::PayloadBounds);
        }

        // 6. Обчислення SHA-256 корисного навантаження
        uint8_t calculatedSha[Sha256SizeBytes];
        if (!crypto_sha256(payload.data(), static_cast<uint32_t>(payload.size()), calculatedSha)) {
            return std::unexpected(ValidationError::HashMismatch);
        }

        if (std::memcmp(calculatedSha, header.payloadSha256, Sha256SizeBytes) != 0) {
            return std::unexpected(ValidationError::HashMismatch);
        }

        // 7. Верифікація криптографічного підпису заголовка
        uint8_t headerHash[Sha256SizeBytes];
        constexpr size_t SignedBytes = sizeof(Header) - SignatureSizeBytes - sizeof(Header::reserved);

        if (!crypto_sha256(reinterpret_cast<const uint8_t*>(&header), static_cast<uint32_t>(SignedBytes), headerHash)) {
            return std::unexpected(ValidationError::SignatureInvalid);
        }

        if (!crypto_verify_signature(rootPublicKey_.data(), headerHash, header.headerSignature)) {
            return std::unexpected(ValidationError::SignatureInvalid);
        }

        return {};
    }

private:
    std::span<const uint8_t> rootPublicKey_;
};

} // namespace emergency
```
:::

## 3. Автомат станів пробного запуску (Trial Boot FSM)

Після успішного проходження валідації завантажувач не переводить новий образ у статус основного остаточно. Замість цього система входить у захищений режим **пробного запуску (Trial Boot)**.

Автомат станів пробного запуску працює за таким алгоритмом:

```
[ IDLE ]
   |
   | (Отримано підписаний hotfix)
   v
[ VALIDATING ] ---> (Помилка підпису/eFuse) ---> [ ABORT / REJECT ]
   |
   | (Валідація OK)
   v
[ FLASHING TO BANK B ]
   |
   | (Запис завершено)
   v
[ TRIAL_BOOT ] -----------------------------------+
   |                                              | (Watchdog reset / HardFault)
   | (Самотест OK + Health Ping на бекенд)        v
   v                                     [ ROLLBACK TO BANK A ]
[ PERMANENT COMMIT ]
   |
   | (Спалювання eFuse лічильника)
   v
[ OPERATIONAL (HOTFIX ACTIVE) ]
```

1. **Ініціалізація пробного стану:** у збережену область пам'яті (RTC Backup Register або збережений сектор Flash) записується лічильник спроб `boot_attempts_left = 3` та прапорець `is_trial_boot = 1`.
2. **Запуск нової прошивки:** завантажувач перемикає вектори переривань і запускає виконання Bank B.
3. **Вікно підтвердження працездатності (Health Confirmation Window):**
   - Нова прошивка ініціалізує критичні драйвери, запускає сторожовий таймер Watchdog і проводить апаратну самодіагностику.
   - Прошивка встановлює захищене TLS-з'єднання з хмарним сервером і надсилає повідомлення `HOTFIX_HEALTH_REPORT_OK`.
   - Отримавши квитанцію (ACK) від сервера, прошивка викликає функцію фіксації: `boot_attempts_left = 0`, `is_trial_boot = 0`.
4. **Аварійний відкат (Automated Rollback):** якщо протягом 120 секунд підтвердження не відбулося (стався `HardFault`, зависання у циклі або спрацював апаратний Watchdog), пристрій скидається. Завантажувач декрементує `boot_attempts_left`. Коли лічильник сягає нуля, завантажувач автоматично конфігурує запуск із попереднього стабільного банку Bank A, повністю виключаючи ризик перетворення пристрою на «цеглину».

## 4. Апаратні особливості спалювання eFuse та захист від збоїв живлення

Процедура фізичного програмування одноразово програваних перемичок (eFuse) є незворотною апаратною транзакцією. Для захисту від пошкодження бітів під час просідання живлення модуль дотримується таких інженерних правил:

1. **Контроль напруги живлення (V_DD / V_PP Threshold):** Перед викликом низькорівневої функції запису eFuse контролер опитує вбудований АЦП та компаратор живлення. Якщо напруга живлення мікроконтролера нижча за 3.15 В, процедура спалювання блокується, оскільки нестабільна напруга може призвести до неповної деградації полікремнієвої перемички і створення метастабільного стану зчитування біта.
2. **Атомарність маски бітів:** Монотонний лічильник організовується у вигляді термометричного або позиційного унітарного коду (наприклад, значення 5 записується як `0b00011111`). Це гарантує, що операція запису лише спалює нові біти з `0` в `1`, ніколи не намагаючись змінити стан уже спалених перемичок.
3. **Фіксація стану в захищеному журналі:** Усі спроби перемикання банків та зміни статусів безпеки фіксуються в енергонезалежному кільцевому буфері діагностики, що дозволяє інженерам після відновлення зв'язку дистанційно відтворити точну хронологію аварійного оновлення.
