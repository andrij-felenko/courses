# 📋 Специфікація маніфесту релізу та інтерфейс публікації артефактів

Цей довідник визначає технічний контракт маніфесту випуску вбудованого програмного забезпечення, двійковий формат префіксного заголовка Secure Boot та інтерфейс взаємодії з корпоративним сховищем релізів.

Маніфест релізу слугує єдиним джерелом правди для всіх учасників процесу життєвого циклу прошивки: системи автоматизованої збірки, апаратного завантажувача мікроконтролера, серверної системи керування парком пристроїв (OTA) та інструментів аудиту безпеки. Відсутність чіткої структурованої специфікації маніфесту призводить до несумісності версій, помилок адресації під час запису пам'яті Flash та неможливості автоматизованої перевірки цифрових підписів.

## Специфікація схеми маніфесту `manifest.json`

Криптографічний маніфест випуску є головним дескриптором пакета оновлення. Він описує цільовий продукт, підтримувані апаратні ревізії, контрольні суми артефактів та політику безпеки. Формат розроблено на основі стандарту JSON Schema Draft 2020-12, що дозволяє проводити автоматичну валідацію структури файлу як на стороні сервера збірки, так і в інструментах заводського контролю.

Кожне поле маніфесту має суворе семантичне призначення. Поле `product_id` запобігає випадковому встановленню прошивки від одного типу пристрою (наприклад, базового сенсорного вузла) на інший (наприклад, центральний шлюз). Поле `security_version` кодує монотонний лічильник захисту від атак типу «відкат версії» (anti-rollback). Якщо виявлено критичну вразливість, це число інкрементується, і завантажувач мікроконтролера назавжди відмовляється приймати старіші збірки.

Масив `images` містить окремий дескриптор для кожної підтримуваної апаратної модифікації. Це дозволяє одному релізу постачати гетерогенні бінарні образи під різні ревізії плат і мікроконтролерів без плутанини у назвах файлів чи адресах секцій пам'яті:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "EmbeddedReleaseManifest",
  "type": "object",
  "required": [
    "schema_version",
    "product_id",
    "version",
    "security_version",
    "commit_hash",
    "timestamp",
    "images",
    "sbom",
    "signatures"
  ],
  "properties": {
    "schema_version": {
      "type": "string",
      "enum": ["1.0", "1.1"],
      "description": "Версія специфікації формату маніфесту"
    },
    "product_id": {
      "type": "string",
      "pattern": "^[a-z0-9-]+$",
      "description": "Унікальний машиночитний ідентифікатор лінійки пристроїв"
    },
    "version": {
      "type": "string",
      "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+(-[a-z0-9.]+)?$",
      "description": "Семантичний номер версії (SemVer 2.0.0)"
    },
    "security_version": {
      "type": "integer",
      "minimum": 0,
      "description": "Монотонний лічильник безпеки для захисту від відкату (anti-rollback)"
    },
    "commit_hash": {
      "type": "string",
      "pattern": "^[0-9a-f]{40}$",
      "description": "Повний 40-символьний SHA-1/SHA-256 хеш коміту вихідного коду"
    },
    "timestamp": {
      "type": "integer",
      "description": "Час створення випуску у форматі Unix Timestamp (SOURCE_DATE_EPOCH)"
    },
    "images": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/ImageDescriptor"
      }
    },
    "sbom": {
      "$ref": "#/$defs/SbomDescriptor"
    },
    "signatures": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/ManifestSignature"
      }
    }
  },
  "$defs": {
    "ImageDescriptor": {
      "type": "object",
      "required": [
        "hardware_target",
        "filename",
        "filesize",
        "sha256",
        "target_slot",
        "flash_address"
      ],
      "properties": {
        "hardware_target": {
          "type": "string",
          "description": "Ідентифікатор цільової апаратної ревізії (наприклад, rev_B, rev_C)"
        },
        "filename": {
          "type": "string",
          "description": "Ім'я підписаного двійкового файлу у складі бандла"
        },
        "filesize": {
          "type": "integer",
          "description": "Розмір двійкового образу в байтах разом із заголовком Secure Boot"
        },
        "sha256": {
          "type": "string",
          "pattern": "^[0-9a-f]{64}$",
          "description": "SHA-256 дайджест повного підписаного двійкового файлу"
        },
        "target_slot": {
          "type": "string",
          "enum": ["slot0", "slot1", "factory", "bootloader"],
          "description": "Призначення розділу Flash-пам'яті мікроконтролера"
        },
        "flash_address": {
          "type": "string",
          "pattern": "^0x[0-9A-Fa-f]{8}$",
          "description": "Фізична адреса базового сектора Flash для запису"
        }
      }
    },
    "SbomDescriptor": {
      "type": "object",
      "required": ["filename", "format", "sha256"],
      "properties": {
        "filename": { "type": "string" },
        "format": { "type": "string", "enum": ["CycloneDX-JSON", "SPDX-JSON"] },
        "sha256": { "type": "string", "pattern": "^[0-9a-f]{64}$" }
      }
    },
    "ManifestSignature": {
      "type": "object",
      "required": ["key_id", "algorithm", "signature"],
      "properties": {
        "key_id": { "type": "string", "description": "Ідентифікатор публічного ключа або відбиток сертифіката" },
        "algorithm": { "type": "string", "enum": ["ECDSA_SHA256", "ED25519", "RSA_PSS_SHA256"] },
        "signature": { "type": "string", "description": "Цифровий підпис маніфесту в кодуванні Base64" }
      }
    }
  }
}
```

## Бінарна структура префіксного заголовка `ImageHeader`

Префіксний заголовок Secure Boot розташовується на початку двійкового образу безпосередньо перед таблицею векторів переривань мікроконтролера. Загальний розмір заголовка становить 128 байтів із вирівнюванням по 4-байтній межі (Little-Endian).

Розміщення заголовка безпосередньо перед кодом дозволяє мікроконтролеру прочитати перші 128 байтів з Flash-пам'яті або з мережевого буфера оновлення ще до початку будь-яких операцій стирання секторів. Завантажувач виконує швидку перевірку магічного числа `magic` та розміру `payload_size`. Якщо вони не відповідають очікуваним значенням, образ відхиляється без витрат часу процесора на ресурсомісткі криптографічні обчислення.

Нижче наведено побайтову розкладку полів заголовка `ImageHeader`:

| Зміщення (Offset) | Розмір (Size) | Поле (Field) | Тип (Type) | Опис та призначення |
|:---|:---|:---|:---|:---|
| `0x00` | 4 байти | `magic` | `uint32_t` | Магічне число `0x53424F54` ("SBOT" у Little-Endian) |
| `0x04` | 4 байти | `version` | `uint32_t` | Упакована версія: `(MAJOR << 24) \| (MINOR << 16) \| (PATCH << 8)` |
| `0x08` | 4 байти | `security_counter`| `uint32_t` | Монотонний лічильник проти відкату версії (Anti-Rollback) |
| `0x0C` | 4 байти | `hw_mask` | `uint32_t` | Бітова маска сумісних апаратних ревізій (Bit 0: Rev A, Bit 1: Rev B...) |
| `0x10` | 4 байти | `payload_size` | `uint32_t` | Точний розмір корисного навантаження (машинного коду) у байтах |
| `0x14` | 32 байти | `payload_digest` | `uint8_t[32]` | SHA-256 дайджест тіла програми без урахування заголовка |
| `0x34` | 64 байти | `signature` | `uint8_t[64]` | Цифровий підпис ECDSA P-256 `(r, s)` або Ed25519 над заголовком і тілом |
| `0x74` | 12 байтів | `reserved` | `uint8_t[12]` | Резервні байти (заповнюються нулями `0x00`) для розширення прапорців |

Поле `hw_mask` використовує бітову логіку: встановлений біт `0` означає підтримку плати Rev A, біт `1` — Rev B, біт `2` — Rev C. Якщо прошивка підтримує ревізії B і C, значення маски становить `0x0006` (`(1 << 1) | (1 << 2)`). Завантажувач порівнює маску зі своїм апаратним ідентифікатором за формулою `(hdr->hw_mask & (1U << HW_REV)) != 0`. Це виключає запуск несумісного коду, який міг би викликати коротке замикання через перепризначені піни GPIO.

Поле `signature` містить 64 байти сирого криптографічного підпису. Для алгоритму ECDSA P-256 воно складається з двох 32-байтних чисел `(r, s)` у порядку байтів Big-Endian або Little-Endian залежно від вимог криптографічної бібліотеки (наприклад, mbedTLS очікує формат Big-Endian для числових компонентів кривої). Для алгоритму Ed25519 підпис є стандартним 64-байтним масивом за RFC 8032.

Поле `reserved` зарезервоване під майбутні прапорці конфігурації безпеки (наприклад, біт шифрування AES-XTS або режим завантаження в зовнішню пам'ять QSPI/OSPI). Наявність фіксованого розміру заголовка у 128 байтів гарантує стабільне зміщення точки входу `Reset_Handler` для апаратного контролера векторів NVIC.

## Опис типів структури на мовах C та C++

Для забезпечення повної бінарної сумісності структури на мовах C та C++ оголошуються з атрибутами пакування `__attribute__((packed))` та явного вирівнювання по межі 4 байтів:

:::tabs
```c
#include <stdint.h>

#define SECURE_BOOT_HEADER_SIZE 128
#define SECURE_BOOT_MAGIC_VALUE 0x53424F54

typedef struct {
    uint32_t magic;
    uint32_t version_packed;
    uint32_t security_counter;
    uint32_t hw_mask;
    uint32_t payload_size;
    uint8_t  payload_digest[32];
    uint8_t  signature[64];
    uint8_t  reserved[12];
} __attribute__((packed, aligned(4))) SecureBootHeader;

_Static_assert(sizeof(SecureBootHeader) == SECURE_BOOT_HEADER_SIZE, "Header size must be 128 bytes");
```
```cpp
#include <cstdint>
#include <array>

namespace release {

inline constexpr size_t SecureBootHeaderSize = 128;
inline constexpr uint32_t SecureBootMagicValue = 0x53424F54;

struct alignas(4) SecureBootHeader {
    uint32_t magic;
    uint32_t versionPacked;
    uint32_t securityCounter;
    uint32_t hwMask;
    uint32_t payloadSize;
    std::array<uint8_t, 32> payloadDigest;
    std::array<uint8_t, 64> signature;
    std::array<uint8_t, 12> reserved;
};

static_assert(sizeof(SecureBootHeader) == SecureBootHeaderSize, "Header size must be 128 bytes");

} // namespace release
```
:::

Використання статичних перевірок `_Static_assert` та `static_assert` гарантує, що компілятор не додасть непередбачених байтів вирівнювання (padding) між полями структури при зміні прапорців оптимізації або при збиранні коду іншим тулчейном.

## REST API корпоративного сховища релізів

Сервіс публікації релізів надає захищений REST API для автоматизованого завантаження артефактів із конвеєра CI/CD та реєстрації нових версій у системі керування оновленнями.

Всі виклики API вимагають автентифікації через протокол OAuth2 / OIDC з використанням тимчасових токенів раннера збірки. Для запобігання дублюванню транзакцій у разі мережевих збоїв кожен запит на створення сесії супроводжується заголовком `X-Idempotency-Key`. Сервер сховища перевіряє claims у токені раннера: ім'я репозиторію, назву гілки та статус верифікації git-тегу.

### 1. Ініціалізація завантаження бандла

Створює тимчасову транзакційну сесію для пакетного завантаження файлів релізу. Сервер виділяє тимчасовий каталог у сховищі та повертає підписані URL-адреси (Presigned URLs) для прямого завантаження бінарників.

- **Метод:** `POST`
- **Шлях:** `/api/v1/releases/staging/init`
- **Заголовки:**
  - `Authorization: Bearer <OIDC_TOKEN>`
  - `Content-Type: application/json`
  - `X-Idempotency-Key: <UUID>`

**Тіло запиту:**

```json
{
  "product_id": "iot-sensor-node",
  "version": "2.4.0",
  "expected_files_count": 3,
  "commit_hash": "7a8f9c4b12d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7"
}
```

**Відповідь (201 Created):**

```json
{
  "session_id": "stg_9f8e7d6c5b4a3210",
  "upload_urls": {
    "manifest.json": "https://storage.internal/staging/stg_9f8e7d6c5b4a3210/manifest.json?sig=...",
    "firmware-revB.signed.bin": "https://storage.internal/staging/stg_9f8e7d6c5b4a3210/firmware-revB.signed.bin?sig=...",
    "firmware.sbom.json": "https://storage.internal/staging/stg_9f8e7d6c5b4a3210/firmware.sbom.json?sig=..."
  },
  "expires_at": 1724806800
}
```

### 2. Атомна фіксація та активація випуску

Перевіряє цілісність усіх завантажених файлів у сесії, перевіряє цифровий підпис маніфесту та переміщує файли у незмінне виробниче сховище. Якщо хоча б один файл відсутній або його контрольна сума не збігається, сесія скасовується, а всі тимчасові об'єкти видаляються.

- **Метод:** `POST`
- **Шлях:** `/api/v1/releases/staging/{session_id}/commit`
- **Заголовки:**
  - `Authorization: Bearer <OIDC_TOKEN>`
  - `Content-Type: application/json`

**Тіло запиту:**

```json
{
  "manifest_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "auto_notify_ota": true
}
```

**Відповідь (200 OK):**

```json
{
  "status": "PUBLISHED",
  "release_id": "rel_iot-sensor-node_v2.4.0",
  "permanent_uri": "s3://releases-prod/iot-sensor-node/v2.4.0/",
  "published_at": 1724803500,
  "ota_campaign_triggered": true
}
```

### Коди помилок API та діагностика

- `400 Bad Request` — невідповідність формату маніфесту, порушення синтаксису SemVer або невідомий ідентифікатор продукту `product_id`.
- `401 Unauthorized` — недійсний, прострочений або підроблений токен OIDC, відсутність необхідних прав запису в конфігурації репозиторію.
- `409 Conflict` — спроба повторної публікації вже наявної незмінної версії (`v2.4.0` вже зафіксовано в системі з політикою незмінності Object Lock).
- `422 Unprocessable Entity` — контрольна сума SHA-256 завантаженого файлу не збігається зі значенням, зафіксованим у тілі маніфесту під час ініціалізації сесії.

Цей API гарантує, що жодна прошивка не з'явиться в каталозі доступних оновлень для кінцевих пристроїв доти, доки сервер повністю не підтвердить валідність криптографічного ланцюжка довіри та не перевірить відповідність усіх бінарних гешів.
