# 📋 Специфікація маніфесту екстреного пакета та заголовка образу

<preknowlist>
- [Наскрізний випуск](root:embedded/naskriznyi-vypusk) — структура бінарного релізного пакета, підпис артефактів та облік компонентів.
- [Захист від відкату](root:sf-security/replay-protection) — монотонні апаратні лічильники версій безпеки для блокування вразливих прошивок.
</preknowlist>

Екстрене оновлення вбудованої системи висуває специфічні вимоги до бінарного формату доставки, які істотно відрізняються від планових випусків. У звичайних умовах агент оновлення може завантажувати великі багатокомпонентні архіви, проводити тривалий парсинг складних файлових систем або очікувати повного циклу перезавантаження користувачем. Під час ліквідації критичної загрози безпеки (0-day) або блокуючого апаратного дефекту система працює в режимі жорсткого дефіциту часу, обмеженої пропускної здатності каналу та деградованого стану зв'язку.

Терміновий пакет (англ. *emergency update package*) використовує компактний, строго детермінований двійковий заголовок `emergency_fw_header_t` фіксованого розміру та супровідний криптографічний JSON-маніфест `emergency_manifest_v1`. Ці структури спроєктовані так, щоб завантажувач (Bootloader) на молодших мікроконтролерах із ліченими кілобайтами оперативної пам'яті міг виконати атомарну перевірку автентичності, цілісності та версії безпеки до початку будь-яких операцій запису у Flash-пам'ять.

## Бінарний заголовок екстреного образу

Бінарний заголовок розміщується на нульовому зміщенні файлу прошивки (`offset 0x00000000`) і має фіксований розмір рівно 256 байтів. Фіксація розміру та вирівнювання за 32-байтною межею дозволяють апаратному контролеру прямого доступу до пам'яті (DMA) вичитувати метадані образу безпосередньо з інтерфейсу SPI Flash або з буфера приймача UART/CAN без використання динамічної пам'яті (heap-free architecture).

:::tabs
```c
#ifndef EMERGENCY_FW_HEADER_H
#define EMERGENCY_FW_HEADER_H

#include <stdint.h>
#include <stdbool.h>

#define EMERGENCY_HEADER_MAGIC      0x454D4759U /* ASCII 'EMGY' (Emergency) */
#define EMERGENCY_HEADER_VERSION    1U
#define EMERGENCY_SIG_SIZE_BYTES    64U         /* ECDSA NIST P-256 (r, s) або Ed25519 */
#define EMERGENCY_SHA256_SIZE_BYTES 32U
#define EMERGENCY_HEADER_SIZE_BYTES 256U

/* Прапорці поведінки екстреного образу */
#define EMERGENCY_FLAG_CRITICAL_CVSS  (1U << 0) /* Критична вразливість безпеки (CVSS >= 9.0) */
#define EMERGENCY_FLAG_FORCE_APPLY    (1U << 1) /* Застосувати негайно без очікування простою */
#define EMERGENCY_FLAG_BURN_ROLLBACK  (1U << 2) /* Вимагає обов'язкового спалювання eFuse OTP */
#define EMERGENCY_FLAG_CANARY_TESTED  (1U << 3) /* Пройдено верифікацію на канарковій підгрупі */
#define EMERGENCY_FLAG_DUAL_CORE_SYNC (1U << 4) /* Містить образ для вторинного мережевого ядра */

#pragma pack(push, 1)
typedef struct {
    uint32_t magic;                   /* Магічне число: 'EMGY' (0x454D4759) */
    uint16_t header_version;          /* Версія формату заголовка (поточна = 1) */
    uint16_t header_size;             /* Загальний розмір заголовка (256 байтів) */
    
    /* Семантичні координати версії */
    uint8_t  ver_major;               /* Мажорна версія */
    uint8_t  ver_minor;               /* Мінорна версія */
    uint16_t ver_patch;               /* Патч-номер (збільшується для hotfix) */
    uint8_t  build_type;              /* 0 = Production Hotfix, 1 = Canary Trial */
    uint32_t commit_hash_prefix;      /* Перші 4 байти хешу коміту Git */
    
    /* Апаратна сумісність та адресація */
    uint32_t target_hw_id;            /* Унікальний ідентифікатор платформи (Platform ID) */
    uint16_t min_hw_rev;              /* Мінімальна сумісна ревізія заліза */
    uint16_t max_hw_rev;              /* Максимальна сумісна ревізія заліза */
    uint16_t target_core_id;          /* 0 = Cortex-M7 (Main), 1 = Cortex-M4 (Radio) */
    
    /* Безпека та захист від відкату */
    uint32_t security_counter;        /* Монотонний лічильник безпеки для eFuse */
    uint32_t flags;                   /* Бітова маска прапорців EMERGENCY_FLAG_* */
    
    /* Параметри корисного навантаження */
    uint32_t payload_offset;          /* Зміщення тіла прошивки від початку файлу */
    uint32_t payload_size;            /* Розмір тіла прошивки в байтах */
    uint32_t payload_entry_point;     /* Адреса точки входу Reset_Handler у Flash */
    uint32_t payload_crc32;           /* Апаратна контрольна сума IEEE 802.3 */
    
    /* Криптографічний контроль цілісності */
    uint8_t  payload_sha256[EMERGENCY_SHA256_SIZE_BYTES]; /* SHA-256 хеш тіла */
    uint8_t  header_signature[EMERGENCY_SIG_SIZE_BYTES];  /* Підпис полів заголовка */
    
    uint8_t  reserved[74];            /* Резерв для майбутніх розширень / вирівнювання */
} emergency_fw_header_t;
#pragma pack(pop)

/* Перевірка розміру структури на етапі компіляції */
_Static_assert(sizeof(emergency_fw_header_t) == EMERGENCY_HEADER_SIZE_BYTES,
               "emergency_fw_header_t must strictly be 256 bytes");

/* Числові коди помилок валідації екстреного заголовка */
typedef enum {
    EMERGENCY_VAL_OK                       = 0,
    EMERGENCY_VAL_ERR_BAD_MAGIC            = -1,
    EMERGENCY_VAL_ERR_UNSUPPORTED_VERSION  = -2,
    EMERGENCY_VAL_ERR_HW_MISMATCH          = -3,
    EMERGENCY_VAL_ERR_CORE_MISMATCH        = -4,
    EMERGENCY_VAL_ERR_ROLLBACK_BLOCKED     = -5,
    EMERGENCY_VAL_ERR_PAYLOAD_BOUNDS       = -6,
    EMERGENCY_VAL_ERR_CRC_MISMATCH         = -7,
    EMERGENCY_VAL_ERR_HASH_MISMATCH        = -8,
    EMERGENCY_VAL_ERR_SIGNATURE_INVALID    = -9,
    EMERGENCY_VAL_ERR_FLASH_WRITE_FAILURE  = -10
} emergency_validation_status_t;

#endif /* EMERGENCY_FW_HEADER_H */
```
```cpp
#pragma once

#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>

namespace emergency {

inline constexpr uint32_t HeaderMagic = 0x454D4759U; // 'EMGY'
inline constexpr uint16_t CurrentHeaderVersion = 1U;
inline constexpr size_t SignatureSizeBytes = 64U;
inline constexpr size_t Sha256SizeBytes = 32U;
inline constexpr size_t HeaderTotalSizeBytes = 256U;

enum class Flag : uint32_t {
    CriticalCvss  = (1U << 0),
    ForceApply    = (1U << 1),
    BurnRollback  = (1U << 2),
    CanaryTested  = (1U << 3),
    DualCoreSync  = (1U << 4),
};

enum class CoreId : uint16_t {
    MainApplication = 0,
    RadioCoprocessor = 1,
};

#pragma pack(push, 1)
struct Header {
    uint32_t magic{HeaderMagic};
    uint16_t headerVersion{CurrentHeaderVersion};
    uint16_t headerSize{static_cast<uint16_t>(HeaderTotalSizeBytes)};
    
    uint8_t  verMajor{0};
    uint8_t  verMinor{0};
    uint16_t verPatch{0};
    uint8_t  buildType{0};
    uint32_t commitHashPrefix{0};
    
    uint32_t targetHwId{0};
    uint16_t minHwRev{0};
    uint16_t maxHwRev{0};
    CoreId   targetCoreId{CoreId::MainApplication};
    
    uint32_t securityCounter{0};
    uint32_t flags{0};
    
    uint32_t payloadOffset{0};
    uint32_t payloadSize{0};
    uint32_t payloadEntryPoint{0};
    uint32_t payloadCrc32{0};
    
    uint8_t  payloadSha256[Sha256SizeBytes]{};
    uint8_t  headerSignature[SignatureSizeBytes]{};
    
    uint8_t  reserved[74]{};
    
    [[nodiscard]] constexpr bool hasFlag(Flag flag) const noexcept {
        return (flags & static_cast<uint32_t>(flag)) != 0;
    }
};
#pragma pack(pop)

static_assert(sizeof(Header) == HeaderTotalSizeBytes, "Header size must strictly be 256 bytes");

enum class ValidationError : int32_t {
    BadMagic            = -1,
    UnsupportedVersion  = -2,
    HardwareMismatch    = -3,
    CoreMismatch        = -4,
    RollbackBlocked     = -5,
    PayloadBounds       = -6,
    CrcMismatch         = -7,
    HashMismatch        = -8,
    SignatureInvalid    = -9,
    FlashWriteFailure   = -10
};

} // namespace emergency
```
:::

## Детальний опис полів заголовка та інваріантів перевірки

Кожне поле структури виконує суворо визначену функцію в ланцюгу забезпечення довіри:

1. `magic` (4 байти): значення `0x454D4759` (ASCII символи `EMGY`). Завантажувач виконує перевірку магічного числа найпершою інструкцією. Якщо число не збігається, обробка негайно припиняється без звернення до криптографічних підсистем, що захищає від випадкової спроби виконання звичайного бінарного файлу або сміття у Flash.
2. `header_version` (2 байти): число `1`. Забезпечує еволюцію формату заголовка у майбутніх версіях SDK без порушення зворотної сумісності зі старими завантажувачами в ROM.
3. `ver_major`, `ver_minor`, `ver_patch` (4 байти сумарно): три числа семантичного версіонування. Для екстреного випуску числа `ver_major` та `ver_minor` зобов'язані строго збігатися з поточною версією у польовому пристрої, а `ver_patch` має бути інкрементований рівно на одиницю (наприклад, перехід із `2.4.0` на `2.4.1`).
4. `commit_hash_prefix` (4 байти): 32-бітний префікс Git-хешу коміту. Дозволяє завантажувачу та службі діагностики зафіксувати точну точку походження бінарника у системі контролю версій без збереження повного 40-символьного рядка.
5. `target_hw_id` (4 байти): унікальний 32-бітний ідентифікатор апаратної плати (наприклад, `0x0000B412` для шлюзу серії G4). Захищає від помилкового завантаження прошивки від сусіднього датчика з тим самим процесором, але іншою розводкою пінів живлення та периферії.
6. `min_hw_rev`, `max_hw_rev` (4 байти): бітова маска або числовий діапазон ревізій друкованої плати (наприклад, від `rev_B` до `rev_C`). Якщо в ході виробництва було замінено модель Flash-пам'яті, прошивка з драйвером старої мікросхеми буде автоматично відхилена новими ревізіями плат.
7. `target_core_id` (2 байти): ідентифікатор цільового процесорного ядра у мультипроцесорних системах (наприклад, STM32WB55 або nRF5340). Дозволяє роздільно оновлювати ядро користувацької програми (Cortex-M7) та ядро мережевого стека BLE/Thread/Zigbee (Cortex-M4).
8. `security_counter` (4 байти): монотонне ціле число версії безпеки. Завантажувач порівнює це число з апаратним лічильником в одноразово програваній пам'яті (eFuse або OTP Flash). **Якщо `security_counter < eFuse_value`, образ категорично відхиляється як потенційна атака відкату.**
9. `flags` (4 байти): бітова конфігурація виконання. Прапорець `EMERGENCY_FLAG_FORCE_APPLY` наказує виконати перезавантаження негайно після перевірки без очікування нічного вікна обслуговування. Прапорець `EMERGENCY_FLAG_BURN_ROLLBACK` вказує завантажувачу виконати апаратне спалювання eFuse після проходження первинної самодіагностики.
10. `payload_offset`, `payload_size` (8 байтів): межі розташування тіла прошивки. Тіло починається строго зі зміщення `0x00000100` (256 байтів). Розмір тіла перевіряється на відповідність фізичним межам секторів банку Flash-пам'яті.
11. `payload_entry_point` (4 байти): адреса вектора скидання `Reset_Handler`. Завантажувач перевіряє, що ця адреса лежить строго всередині адресного простору цільового банку Flash.
12. `payload_sha256` (32 байти): криптографічний хеш виконуваного коду. Обчислюється конвеєром збірки від початку тіла прошивки (`payload_offset`) до його кінця (`payload_offset + payload_size`).
13. `header_signature` (64 байти): цифровий підпис ECDSA NIST P-256 або Ed25519. Підпис накладається на перші 118 байтів заголовка (всі поля від `magic` до `payload_sha256` включно). Оскільки сам хеш корисного навантаження входить до зони підпису заголовка, підпис заголовка криптографічно засвідчує цілісність усього файлу прошивки.

## Специфікація маніфесту екстреного випуску (JSON)

Поряд із двійковим бінарним файлом система автоматизації CI/CD генерує файл маніфесту випуску `emergency_release_manifest.json`. Цей маніфест завантажується на сервер управління парком пристроїв (OTA Management Backend) для маршрутизації оновлення, аудиту відповідності та керування політикою канаркового розгортання.

```json
{
  "manifest_schema_version": "1.0.0",
  "release_type": "EMERGENCY_HOTFIX",
  "incident_tracking": {
    "cve_list": ["CVE-2026-4419"],
    "cvss_score_base": 9.8,
    "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
    "emergency_ticket_id": "SEC-INCIDENT-8842",
    "authorized_by": [
      {
        "role": "Security Operations Lead",
        "key_fingerprint": "SHA256:4f8a9b2c...01",
        "timestamp_utc": "2026-08-28T01:10:00Z"
      },
      {
        "role": "Chief Technology Officer",
        "key_fingerprint": "SHA256:7e1d3c5a...99",
        "timestamp_utc": "2026-08-28T01:12:30Z"
      }
    ]
  },
  "compatibility": {
    "target_platform_id": "0x0000B412",
    "platform_name": "GATEWAY-PRO-G4",
    "supported_hardware_revisions": ["revB", "revC"],
    "required_base_firmware": {
      "major": 2,
      "minor": 4,
      "patch": 0
    }
  },
  "target_version": {
    "semantic_string": "2.4.1",
    "major": 2,
    "minor": 4,
    "patch": 1,
    "security_version_counter": 5,
    "git_commit_sha": "7a8f9c4b12d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7"
  },
  "artifact_details": {
    "binary_filename": "firmware_hotfix_v2.4.1_revB.bin",
    "binary_size_bytes": 393472,
    "header_size_bytes": 256,
    "payload_size_bytes": 393216,
    "payload_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "payload_crc32": "0x8F32C19E",
    "storage_url": "https://ota-cdn.embedded-systems.ua/releases/v2.4.1/firmware_hotfix_v2.4.1_revB.bin"
  },
  "canary_rollout_rules": {
    "phase_1_canary_percent": 1.5,
    "phase_1_soak_time_seconds": 7200,
    "phase_2_expansion_percent": 20.0,
    "phase_2_interval_seconds": 3600,
    "phase_3_full_fleet_percent": 100.0,
    "circuit_breaker_thresholds": {
      "max_watchdog_reset_rate_percent": 0.05,
      "max_install_failure_rate_percent": 0.10,
      "max_network_drop_rate_percent": 0.20
    }
  },
  "cryptographic_envelope": {
    "signing_algorithm": "ECDSA_P256_SHA256",
    "hsm_key_identifier": "hsm-slot-04-prod-emergency-2026",
    "manifest_signature_base64": "MEYCIQDx4k..."
  }
}
```

## Таблиця помилок верифікації та поведінка завантажувача

У разі виникнення будь-якої невідповідності під час обробки пакета завантажувач зобов'язаний зафіксувати числовий код помилки у статичному журналі діагностики (у збереженій ділянці RTC SRAM або FRAM) та вжити захисних заходів:

| Код помилки | Константа | Причина виникнення | Дія системи та наслідки |
|---|---|---|---|
| `-1` | `EMERGENCY_VAL_ERR_BAD_MAGIC` | Перші 4 байти не дорівнюють `0x454D4759`. | Відхилення файлу. Запис у Flash блокується. |
| `-2` | `EMERGENCY_VAL_ERR_UNSUPPORTED_VERSION` | Поле `header_version` має непідтримуване значення. | Відхилення файлу. Повідомлення бекенду про застарілий завантажувач. |
| `-3` | `EMERGENCY_VAL_ERR_HW_MISMATCH` | `target_hw_id` або ревізія не відповідають даній платі. | Відхилення файлу. Запобігає пошкодженню чужої конфігурації пінів. |
| `-4` | `EMERGENCY_VAL_ERR_CORE_MISMATCH` | Образ призначений для іншого процесорного ядра. | Маршрутизація образу у пам'ять відповідного сопроцесора. |
| `-5` | `EMERGENCY_VAL_ERR_ROLLBACK_BLOCKED` | `security_counter` менший за апаратне значення в eFuse. | **Критичне відхилення.** Блокування атаки відкату (downgrade attack). |
| `-6` | `EMERGENCY_VAL_ERR_PAYLOAD_BOUNDS` | Розмір тіла перевищує фізичний розмір банку Flash. | Відхилення файлу. Запобігає перетиранню сусідніх секторів конфігурації. |
| `-7` | `EMERGENCY_VAL_ERR_CRC_MISMATCH` | Апаратна контрольна сума CRC-32 після запису не збіглася. | Помилка шини або дефект пам'яті. Очищення цільового банку. |
| `-8` | `EMERGENCY_VAL_ERR_HASH_MISMATCH` | Обчислений SHA-256 не збігається з полем `payload_sha256`. | Відхилення образу. Пошкодження файлу під час передачі мережею. |
| `-9` | `EMERGENCY_VAL_ERR_SIGNATURE_INVALID` | Відкритий ключ виробника не підтвердив цифровий підпис. | **Критичне відхилення.** Спроба завантаження неавторизованого коду. |
| `-10` | `EMERGENCY_VAL_ERR_FLASH_WRITE_FAILURE` | Апаратний збій контролера Flash під час програмування. | Фіксація апаратного дефекту мікросхеми. Залишення активним старого банку. |

## Апаратні обмеження пам'яті та вирівнювання сторінок Flash

Фізична організація енергонезалежної Flash-пам'яті накладає суворі апаратні обмеження на процес запису екстреного пакета:

1. **Вирівнювання сторінок (Page/Sector Alignment):** Поле `payload_offset` строго дорівнює `256` байтам, що збігається з мінімальним розміром сторінки програмування більшості мікросхем NOR Flash (наприклад, Winbond W25Q або внутрішня Flash STM32G4). Це усуває необхідність додаткового зсуву буферів в ОЗП під час поблокового запису.
2. **Атомарність оновлення дескриптора:** Заголовок образу записується у Flash-пам'ять в останню чергу, після повної верифікації корисного навантаження в пасивному банку. Якщо живлення пристрою зникає в процесі запису коду, завантажувач під час наступного старту бачить стертий або неповний заголовок і не робить спроб передачі керування пошкодженому коду.
3. **Апаратні слоти ключів у захищеному сховищі (Secure Storage):** Відкритий ключ для перевірки `header_signature` зчитується із захищеного сховища чипа (наприклад, Secure User Flash або апаратний криптографічний чип ATECC608B / STSAFE-A110). Використання публічних ключів із загального адресного простору Flash заборонено специфікацією.

Ця специфікація забезпечує вичерпну несуперечливість двійкових контрактів між сервером підпису, системою розгортання OTA та вбудованим завантажувачем мікроконтролера.
