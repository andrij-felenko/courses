# 📋 Специфікація канонічної схеми подій безпеки та контракт інтерфейсу WORM

Цей документ містить технічну специфікацію структури записів аудиту безпеки, схему валідації полів за стандартом JSON Schema, опис бінарного представлення для нульового копіювання (Zero-Copy) мовами C та C++, а також формальний контракт інтерфейсу незмінного сховища WORM (Write Once, Read Many).

## 1. Канонічна модель запису аудиту (5W1H Schema)

Кожна подія безпеки в системі повинна серіалізуватися в строго типізований формат, що містить повний контекст операції та криптографічні метадані.

Схема побудована за принципом криміналістичної повноти: кожен запис мусить містити достатньо інформації для повної реконструкції стану без звернення до зовнішніх змінних баз даних, які зловмисник міг модифікувати.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "SecurityAuditEvent",
  "type": "object",
  "required": [
    "event_id",
    "timestamp_utc",
    "sequence_number",
    "actor",
    "action",
    "target",
    "security_context",
    "outcome",
    "integrity"
  ],
  "properties": {
    "event_id": {
      "type": "string",
      "format": "uuid",
      "description": "Унікальний 128-бітний ідентифікатор події (UUIDv4 або ULID)"
    },
    "timestamp_utc": {
      "type": "string",
      "format": "date-time",
      "description": "Мітка фізичного часу UTC у форматі ISO 8601 з наносекундами"
    },
    "sequence_number": {
      "type": "integer",
      "minimum": 0,
      "description": "Монотонно зростаючий 64-бітний лічильник вузла"
    },
    "actor": {
      "type": "object",
      "required": ["principal_id", "principal_type", "authenticated"],
      "properties": {
        "principal_id": { "type": "string" },
        "principal_type": { "type": "string", "enum": ["USER", "SERVICE", "ANONYMOUS", "SYSTEM"] },
        "authenticated": { "type": "boolean" },
        "roles": { "type": "array", "items": { "type": "string" } },
        "session_id": { "type": "string" },
        "client_ip": { "type": "string", "format": "ipv4" }
      }
    },
    "action": {
      "type": "object",
      "required": ["verb", "category"],
      "properties": {
        "verb": { "type": "string", "description": "Дія у форматі domain.resource.operation (напр. iam.user.elevate)" },
        "category": { "type": "string", "enum": ["AUTH", "ACCESS_CONTROL", "DATA_MUTATION", "CONFIG_CHANGE", "SYSTEM_SHUTDOWN"] }
      }
    },
    "target": {
      "type": "object",
      "required": ["resource_id", "resource_type"],
      "properties": {
        "resource_id": { "type": "string" },
        "resource_type": { "type": "string" },
        "pre_state_hash": { "type": "string" },
        "post_state_hash": { "type": "string" }
      }
    },
    "security_context": {
      "type": "object",
      "required": ["tls_version", "mfa_verified"],
      "properties": {
        "tls_version": { "type": "string" },
        "cipher_suite": { "type": "string" },
        "mfa_verified": { "type": "boolean" },
        "caller_process_pid": { "type": "integer" }
      }
    },
    "outcome": {
      "type": "object",
      "required": ["status"],
      "properties": {
        "status": { "type": "string", "enum": ["SUCCESS", "DENIED", "ERROR"] },
        "error_code": { "type": "string" },
        "reason": { "type": "string" }
      }
    },
    "integrity": {
      "type": "object",
      "required": ["key_epoch", "prev_entry_hash", "entry_signature"],
      "properties": {
        "key_epoch": { "type": "integer", "minimum": 0 },
        "prev_entry_hash": { "type": "string", "pattern": "^[0-9a-fA-F]{64}$" },
        "entry_signature": { "type": "string", "pattern": "^[0-9a-fA-F]{64}$" }
      }
    }
  }
}
```

### Семантичні правила валідації

1. **Ідентифікатор суб'єкта (Actor Principal):** Якщо дія виконується від імені сервісного облікового запису або через делегування повноважень (`impersonation`), структура `actor` зобов'язана містити вкладений блок `delegated_by` із зазначенням первинного користувача.
2. **Незмінність мітки часу:** Поле `timestamp_utc` фіксується виключно за шкалою всесвітнього координованого часу (UTC). Локальні зміщення часових поясів заборонені для усунення плутанини при переході на літній/зимовий час.
3. **Гешування стану ресурсу:** Поля `pre_state_hash` та `post_state_hash` містять криптографічні геші SHA-256 від канонічного JSON-представлення цільового об'єкта до та після виконання операції. Це дозволяє довести факт несанкціонованої мутації без розкриття повного тіла великих документів.

## 2. Бінарне представлення для ядра та високошвидкісних систем

Для високонавантажених сервісів, модулів ядра операційної системи та драйверів накопичувачів використовується бінарний заголовок фіксованої довжини (128 байтів), вирівняний по 64-бітній межі для запобігання накладним витратам на невирівняний доступ до пам'яті.

:::tabs
```c
#include <stdint.h>

#define AUDIT_MAGIC 0x41554454 /* 'AUDT' */
#define HASH_SIZE 32

#pragma pack(push, 1)

struct audit_record_header {
    uint32_t magic;                 /* Магічні байти 'AUDT' */
    uint16_t version;               /* Версія бінарного формату (напр. 1) */
    uint16_t header_size;           /* Розмір заголовка в байтах (128) */
    uint64_t sequence_number;       /* Монотонний порядковий номер запису */
    uint64_t timestamp_nanos;       /* Наносекунди від Unix Epoch (UTC) */
    uint32_t payload_length;        /* Довжина корисного навантаження (JSON/Protobuf) */
    uint32_t key_epoch;             /* Поточна епоха Forward-Secure ключа */
    uint8_t  prev_hash[HASH_SIZE];  /* SHA-256 геш попереднього запису */
    uint8_t  signature[HASH_SIZE];  /* HMAC-SHA256 підпис поточного запису */
    uint8_t  reserved[16];          /* Резерв для майбутніх розширень (вирівнювання) */
};

#pragma pack(pop)
```
```cpp
#include <cstdint>
#include <array>
#include <span>

namespace security::audit {

constexpr uint32_t AuditMagic = 0x41554454; /* 'AUDT' */
constexpr size_t HashSize = 32;

#pragma pack(push, 1)
struct AuditRecordHeader {
    uint32_t magic{AuditMagic};
    uint16_t version{1};
    uint16_t header_size{sizeof(AuditRecordHeader)};
    uint64_t sequence_number{0};
    uint64_t timestamp_nanos{0};
    uint32_t payload_length{0};
    uint32_t key_epoch{0};
    std::array<uint8_t, HashSize> prev_hash{};
    std::array<uint8_t, HashSize> signature{};
    std::array<uint8_t, 16> reserved{};
};
#pragma pack(pop)

static_assert(sizeof(AuditRecordHeader) == 128, "Header size must be exactly 128 bytes");

} // namespace security::audit
```
:::

## 3. Контракт програмного інтерфейсу WORM (libworm_audit)

Бібліотека надає абстракцію над апаратними носіями WORM та захищеними хмарними сховищами. Клієнтський інтерфейс гарантує атомарність операцій, автоматичне просування ключів та захист від блокувань.

### 3.1. Типи та коди помилок

| Код повернення | Числове значення | Опис |
| :--- | :--- | :--- |
| `WORM_SUCCESS` | `0` | Операція успішно завершена. |
| `WORM_ERR_INVALID_PARAM` | `-1` | Передано некоректний вказівник або нульову довжину. |
| `WORM_ERR_DISK_FULL` | `-2` | Сховище заповнене (спрацьовує політика Fail-Secure). |
| `WORM_ERR_CHAIN_BROKEN` | `-3` | Виявлено розрив або фальсифікацію геш-ланцюга. |
| `WORM_ERR_SIGNATURE_FAILED`| `-4` | Не збігся криптографічний HMAC-підпис запису. |
| `WORM_ERR_KEY_EXHAUSTED` | `-5` | Ліміт епох односпрямованого храповика вичерпано. |
| `WORM_ERR_IO` | `-6` | Помилка дискового введення-виведення або втрата мережі. |

### 3.2. Сигнатури функцій та класів

:::tabs
```c
#include <stddef.h>
#include <stdint.h>

typedef struct worm_context worm_context_t;

/* Ініціалізація клієнта журналу аудиту */
int worm_audit_init(worm_context_t** ctx, const char* storage_path, const uint8_t* master_key_32b);

/* Атомарний запис події з оновленням геш-ланцюга та просуванням ключа */
int worm_audit_append(worm_context_t* ctx, const uint8_t* payload, size_t length, uint64_t* out_seq);

/* Синхронізація буферів на енергонезалежний носій (fsync/O_SYNC) */
int worm_audit_flush(worm_context_t* ctx);

/* Верифікація діапазону записів на предмет незмінності та коректності підписів */
int worm_audit_verify(const char* log_file_path, const uint8_t* base_key_32b, uint64_t from_seq, uint64_t to_seq);

/* Звільнення ресурсів та безпечне затирання секретів у пам'яті */
void worm_audit_close(worm_context_t* ctx);
```
```cpp
#include <string_view>
#include <span>
#include <memory>
#include <expected>
#include <cstdint>

namespace security::audit {

enum class WormError {
    InvalidParam = -1,
    DiskFull = -2,
    ChainBroken = -3,
    SignatureFailed = -4,
    KeyExhausted = -5,
    IoError = -6
};

class IWormAuditStorage {
public:
    virtual ~IWormAuditStorage() = default;

    virtual std::expected<uint64_t, WormError> append(std::span<const uint8_t> payload) = 0;
    virtual std::expected<void, WormError> flush() = 0;
    virtual std::expected<void, WormError> verifyRange(uint64_t from_seq, uint64_t to_seq) const = 0;
};

std::expected<std::unique_ptr<IWormAuditStorage>, WormError>
createWormStorage(std::string_view storage_path, std::span<const uint8_t, 32> master_key);

} // namespace security::audit
```
:::

### 3.3. Гарантії та інваріанти

1. **Гарантія незмінності (Immutability):** Після успішного повернення з `worm_audit_append` та виклику `worm_audit_flush` запис не може бути змінений жодним процесом у системі. Будь-яка спроба перезапису сектора призведе до апаратної помилки вводу-виводу.
2. **Гарантія безпеки минулого (Forward Secrecy):** Ключ `K_i`, використаний для підпису запису `i`, негайно затирається в пам'яті функцією `explicit_bzero` або деструктором `SecureBuffer`. Знаючи поточний стан пам'яті в момент `T`, неможливо згенерувати дійсний підпис для будь-якого запису до моменту `T`.
3. **Строга монотонність лічильника:** Поле `sequence_number` строго монотонне (`seq_{i} = seq_{i-1} + 1`). Пропуски або дублювання номерів сигналізують про спробу фальсифікації або видалення блоків.

## 4. Канонізація структурованих даних (RFC 8785 JSON Canonicalization Scheme)

Перед обчисленням криптографічного гешу корисне навантаження запису аудиту повинно бути приведене до канонічного вигляду. Оскільки формати JSON допускають різний порядок ключів, довільні пробільні символи та різні форми запису чисел, наївне гешування призводить до розбіжностей під час верифікації на різних мовах програмування.

Стандарт RFC 8785 визначає такі обов'язкові правила канонізації:
- **Лексикографічне сортування ключів:** Усі ключі JSON-об'єктів сортуються за кодовими точками UTF-16 у порядку зростання.
- **Видалення зайвих пробілів:** Пробільні символи між ключами, двокрапками, комами та значеннями повністю видаляються.
- **Детерміноване представлення чисел:** Цілі числа записуються без ведучих нулів; дійсні числа записуються без завершальних нулів у дробовій частині. Експоненційний запис дозволений лише для чисел, що виходять за межі стандартної точності IEEE 754.
- **Нормалізація рядків Unicode:** Усі символьні рядки приводяться до форми нормалізації NFC (Normalization Form C) з екрануванням лише обов'язкових символів (лапки, зворотний слеш, керуючі символи ASCII від 0x00 до 0x1F).

## 5. Правила маскування конфіденційної інформації (PII Redaction Engine)

Журнал аудиту призначений для контролю безпеки, а не для накопичення конфіденційних відомостей. Збереження немодифікованих секретів у логах порушує вимоги стандартів GDPR, PCI-DSS та HIPAA.

Шлюз санітизації застосовує три стратегії обробки полів:
1. **Повне видалення (Blacklisting):** Поля, що містять паролі, закриті криптографічні ключі, сесійні токени та CVV/CVC-коди банківських карток, безумовно замінюються на константний рядок `[REDACTED]`.
2. **Часткове маскування (Masking):** Для номерів банківських карток (PAN) зберігаються лише перші шість цифр (BIN) та останні чотири цифри номера (`4111 22** **** 1234`), що дозволяє фінансовому моніторингу ідентифікувати емітента без ризику компрометації платіжних даних.
3. **Криптографічна псевдонімізація (HMAC Pseudonymization):** Для чутливих ідентифікаторів користувачів (наприклад, номерів соціального страхування або паспортних даних) генерується детермінований псевдонім за схемою `HMAC-SHA256(Secret_Salt, User_ID)`. Це дозволяє аналітикам безпеки корелювати події одного й того самого суб'єкта в розподіленій системі, не маючи доступу до його реальних персональних даних.

## 6. Низькорівневий життєвий цикл сесії WORM-запису

Взаємодія прикладного сервісу з рушієм незмінного запису підпорядковується суворому скінченному автомату станів:

1. **Ініціалізація (`worm_audit_init`):** Виділяється пам'ять під контекст `worm_context_t`. Початковий таємний ключ `master_key_32b` захищається системним викликом `mlock()`, щоб запобігти витісненню секрету на диск у файл підкачки (swap).
2. **Транзакційний запис (`worm_audit_append`):** Запис додається в кільцевий буфер пам'яті, генерується HMAC-підпис та просувається храповик Forward-Secure.
3. **Енергонезалежна фіксація (`worm_audit_flush`):** Буфери скидаються на апаратний носій WORM за допомогою системного виклику `fsync()`. Повернення значення `WORM_SUCCESS` є гарантією юридичної незмінності запису.
4. **Завершення роботи (`worm_audit_close`):** Контекст очищується, усі ключі в пам'яті перезаписуються нулями (`explicit_bzero`), після чого пам'ять звільняється через `munlock()` та `free()`.
