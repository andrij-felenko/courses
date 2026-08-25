# 📋 Специфікація інтерфейсного контракту та валідатора межі довіри

У взаємодії між компонентами з різними рівнями довіри інтерфейс (API) є єдиним захисним бар'єром, що відділяє ізольований контур від зовнішнього впливу. Якщо протокол обміну допускає неоднозначність трактування полів, динамічні типи без перевірки меж або надлишковий функціонал, межа довіри розмивається, відкриваючи можливість для ін'єкцій та атак на відмову в обслуговуванні.

Ця специфікація визначає бінарний протокол та програмний контракт шлюзу перетину межі довіри (Trust Boundary Gateway Contract): структуру бінарних пакетів, правила канонізації та санітизації, стан скінченного автомата валідатора, таблицю кодів помилок та ідіоматичні інтерфейси мовами C та C++.

## Життєвий цикл бінарного повідомлення на межі довіри

Коли потік байтів надходить із менш довіреного середовища, він підпорядковується суворому конвеєру обробки:

1. **Фаза кадрування (Framing):** Шлюз зчитує фіксований заголовок кадру розміром 16 байтів. Перевіряється магічне число `Magic` та версія протоколу. Якщо розмір повідомлення виходить за межі допустимого діапазону (0..4096 байтів), з'єднання негайно скидається без виділення динамічної пам'яті.
2. **Фаза цілісності (Integrity Check):** Після отримання заявленого обсягу корисного навантаження шлюз зчитує 4-байтове поле контрольної суми CRC32-C. Обчислена за заголовком і тілом сума повинна збігатися байт-у-байт. Це відсікає пошкоджені або спотворені пакети ще до етапу семантичного розбору.
3. **Фаза нормалізації та канонізації (Canonicalization):** Якщо корисне навантаження містить текстові рядки, шляхи до файлів або ідентифікатори ресурсів, вони приводяться до єдиної канонічної форми.
4. **Фаза типізованої валідації (Validation):** Поля повідомлення копіюються в типізовану внутрішню структуру `SafeMessage`. Числові значення перевіряються на допустимі діапазони, а бітові прапорці звіряються з маскою дозволених операцій.
5. **Фаза диспетчеризації (Dispatching):** Очищене й перевірене повідомлення передається бізнес-логіці довіреного контуру. Відповідь формується за аналогічною схемою кадрування з встановленням прапорця `IS_RESPONSE`.

## Формат бінарного кадру (Wire Protocol Frame)

Обмін між контурами безпеки здійснюється фіксованими бінарними кадрами, вирівняними по 8-байтовій межі:

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|          Magic (0x53454355)   |          Version (1)          |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|          Opcode (u16)         |          Flags (u16)          |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                         Sequence ID (u32)                     |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                        Payload Length (u32)                   |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                                                               |
+                    Payload Data (0..4096 bytes)               +
|                                                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                        CRC32-C Checksum                       |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

### Детальний опис полів заголовка кадру

| Поле | Тип | Зсув (байти) | Опис та правила валідації |
| :--- | :--- | :--- | :--- |
| `Magic` | `uint16_t` | 0 | Фіксована магічна константа `0x5345` ("SE"). Незбіг свідчить про спотворення протоколу або спробу ін'єкції чужого трафіку. |
| `Version` | `uint16_t` | 2 | Версія протоколу. Підтримується тільки версія `1`. Інші значення відхиляються для виключення семантичного розриву версій. |
| `Opcode` | `uint16_t` | 4 | Код операції: `0x0001` (PING), `0x0002` (PARSE), `0x0003` (VALIDATE), `0x0004` (EXECUTE). |
| `Flags` | `uint16_t` | 6 | Бітові прапорці: `0x0001` (ENCRYPTED), `0x0002` (COMPRESSED), `0x0004` (IS_RESPONSE). |
| `Sequence ID` | `uint32_t` | 8 | Монотонний лічильник повідомлень для запобігання атакам повторного відтворення. |
| `Payload Length` | `uint32_t` | 12 | Точна довжина корисного навантаження (від 0 до 4096 байтів). Значення > 4096 заборонені. |
| `Payload Data` | `uint8_t[]` | 16 | Сирі дані повідомлення, розмір яких строго дорівнює `Payload Length`. |
| `Checksum` | `uint32_t` | 16 + N | Контрольна сума CRC32-C над заголовком і тілом повідомлення. |

## Правила канонізації вхідних даних

Канонізація є обов'язковою передумовою будь-якої бізнес-перевірки. Неканонізовані дані призводять до обходу регулярних виразів та фільтрів безпеки.

### 1. Нормалізація шляхів файлової системи
- Усі символи зворотного слешу `\` замінюються на прямий слеш `/`.
- Послідовності повторюваних слешів `//` згортаються в один `/`.
- Сегменти поточного каталогу `/./` видаляються.
- Сегменти виходу в батьківський каталог `/../` резольвються строго всередині базового кореня. Якщо вихід за межі кореня неможливий, шлях відхиляється з кодом помилки `ERR_CANONICALIZATION_FAIL`.
- Перевіряється повна відсутність нульових байтів `\0` всередині рядка шляху.

### 2. Нормалізація текстових рядків та кодувань Unicode
- Усі рядкові поля декодуються строго як UTF-8. Будь-які некоректні послідовності байтів (Invalid UTF-8) або наддовгі форми кодування символів (Overlong UTF-8 encodings) відкидаються.
- Рядки приводяться до канонічної форми нормалізації **NFC (Unicode Normalization Form C)**. Це виключає ситуації, коли однаковий візуальний символ представлений різними комбінаціями базових символів та діакритичних знаків.
- Видаляються невидимі керівні символи (ASCII 0..31), крім дозволених символів перенесення рядка (`\n`, `\r`, `\t`).

## Еволюція схеми та безпечне оновлення версій інтерфейсу

Під час розвитку системи компоненти по різні боки межі довіри оновлюються несинхронно: клієнт може використовувати нову версію схеми, тоді як сервер або апаратний анклав підтримує лише попередню. Щоб уникнути вразливостей, застосовують такі правила еволюції:

1. **Суворе відхилення невідомих полів (Reject Unknown Fields):** На відміну від звичайних сервісів Web API, де невідомі поля JSON часто ігноруються, на межі безпеки наявність невідомих полів або нерозпізнаних опкодів повинна викликати негайне відхилення кадру (`ERR_SCHEMA_VIOLATION`). Ігнорування невідомих полів дозволяє зловмиснику пронести шкідливе навантаження через фільтр до компонентів наступного контуру, які можуть підтримувати ці приховані поля.
2. **Незмінність ідентифікаторів полів:** Опкоди та зміщення полів у бінарних структурах ніколи не змінюють свого призначення між версіями. Застарілі поля позначаються як зарезервовані (`reserved`), а не видаляються.
3. **Квоти ресурсів та захист від перевантаження (Backpressure):** Шлюз межі контролює швидкість надходження повідомлень (Rate Limiting). При перевищенні ліміту 1000 запитів/с шлюз повертає стан зайнятості та не виділяє ресурси під десеріалізацію.

## Скінченний автомат валідатора межі (Boundary State Machine)

Перетин межі довіри підпорядковується детермінованому скінченному автомату, який виключає обробку даних за межами валідного контексту:

```
[СТАН: IDLE]
     │
     ▼ (Надходження перших 16 байтів)
[СТАН: HEADER_PARSED] ──(Помилка: Magic/Version/Length)──> [СТАН: FAULT_DROP]
     │
     ▼ (Усі байти Payload прочитано)
[СТАН: PAYLOAD_LOADED]
     │
     ▼ (Обчислення CRC32-C)
[СТАН: CHECKSUM_VERIFIED] ──(Незбіг CRC32)──> [СТАН: FAULT_DROP]
     │
     ▼ (Канонізація та семантична перевірка)
[СТАН: DISPATCH_READY]
     │
     ▼ (Виконання операції в довіреному контурі)
[СТАН: SUCCESS_RESPOND]
```

### Коди помилок шлюзу (Gateway Error Codes)

| Код помилки | Числове значення | Опис причини | Дія шлюзу |
| :--- | :--- | :--- | :--- |
| `GATEWAY_OK` | `0x0000` | Операція успішно виконана | Повернення результату |
| `ERR_BAD_MAGIC` | `0x0001` | Магічний заголовок не збігається | Знищення з'єднання, лог |
| `ERR_UNSUPPORTED_VERSION` | `0x0002` | Версія протоколу не підтримується | Відхилення запиту |
| `ERR_PAYLOAD_TOO_LARGE` | `0x0003` | Довжина перевищує ліміт 4096 байтів | Скидання буфера, тривога |
| `ERR_CHECKSUM_MISMATCH` | `0x0004` | Помилка контрольної суми CRC32 | Відхилення кадру |
| `ERR_SCHEMA_VIOLATION` | `0x0005` | Порушення інваріантів бізнес-схеми | Відмова виконання |
| `ERR_CANONICALIZATION_FAIL`| `0x0006` | Неможливо нормалізувати шлях чи рядок | Відмова виконання |
| `ERR_ACCESS_DENIED` | `0x0007` | Недостатньо повноважень суб'єкта | Аудит відмови |

## Програмний інтерфейс валідатора мовами C та C++

Наведемо структури даних, сигнатури функцій та еталонну реалізацію валідатора межі довіри.

:::tabs
```c
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <string.h>

#define BOUNDARY_MAGIC      0x5345
#define BOUNDARY_VERSION    1
#define MAX_PAYLOAD_SIZE    4096

typedef enum {
    GATEWAY_OK = 0,
    ERR_BAD_MAGIC = 1,
    ERR_UNSUPPORTED_VERSION = 2,
    ERR_PAYLOAD_TOO_LARGE = 3,
    ERR_CHECKSUM_MISMATCH = 4,
    ERR_SCHEMA_VIOLATION = 5,
    ERR_CANONICALIZATION_FAIL = 6,
    ERR_ACCESS_DENIED = 7
} GatewayErrorCode;

#pragma pack(push, 1)
typedef struct {
    uint16_t magic;
    uint16_t version;
    uint16_t opcode;
    uint16_t flags;
    uint32_t sequence_id;
    uint32_t payload_len;
} BoundaryFrameHeader;
#pragma pack(pop)

typedef struct {
    BoundaryFrameHeader header;
    uint8_t payload[MAX_PAYLOAD_SIZE];
    uint32_t checksum;
} ParsedBoundaryMessage;

/* Простий генератор CRC32 для ілюстрації верифікації */
static uint32_t compute_crc32(const uint8_t *data, size_t len) {
    uint32_t crc = 0xFFFFFFFF;
    for (size_t i = 0; i < len; ++i) {
        crc ^= data[i];
        for (int j = 0; j < 8; ++j) {
            crc = (crc >> 1) ^ (0xEDB88320 & (-(crc & 1)));
        }
    }
    return ~crc;
}

/* Інтерфейсний контракт валідації вхідного бінарного кадру */
GatewayErrorCode validate_boundary_frame(
    const uint8_t *raw_stream,
    size_t stream_len,
    ParsedBoundaryMessage *out_msg
) {
    if (raw_stream == NULL || out_msg == NULL) {
        return ERR_SCHEMA_VIOLATION;
    }

    /* 1. Перевірка мінімального розміру для розміщення заголовка та CRC */
    if (stream_len < sizeof(BoundaryFrameHeader) + sizeof(uint32_t)) {
        return ERR_SCHEMA_VIOLATION;
    }

    /* 2. Копіювання заголовка у локальну пам'ять (Single Copy) */
    BoundaryFrameHeader local_hdr;
    memcpy(&local_hdr, raw_stream, sizeof(BoundaryFrameHeader));

    /* 3. Валідація магічного числа та версії */
    if (local_hdr.magic != BOUNDARY_MAGIC) {
        return ERR_BAD_MAGIC;
    }
    if (local_hdr.version != BOUNDARY_VERSION) {
        return ERR_UNSUPPORTED_VERSION;
    }

    /* 4. Контроль довжини корисного навантаження */
    if (local_hdr.payload_len > MAX_PAYLOAD_SIZE) {
        return ERR_PAYLOAD_TOO_LARGE;
    }

    size_t expected_total_size = sizeof(BoundaryFrameHeader) + local_hdr.payload_len + sizeof(uint32_t);
    if (stream_len < expected_total_size) {
        return ERR_SCHEMA_VIOLATION;
    }

    /* 5. Перевірка контрольної суми */
    uint32_t expected_crc = compute_crc32(raw_stream, sizeof(BoundaryFrameHeader) + local_hdr.payload_len);
    uint32_t packet_crc;
    memcpy(&packet_crc, raw_stream + sizeof(BoundaryFrameHeader) + local_hdr.payload_len, sizeof(uint32_t));

    if (expected_crc != packet_crc) {
        return ERR_CHECKSUM_MISMATCH;
    }

    /* 6. Заповнення безпечного типізованого об'єкта */
    out_msg->header = local_hdr;
    memcpy(out_msg->payload, raw_stream + sizeof(BoundaryFrameHeader), local_hdr.payload_len);
    out_msg->checksum = packet_crc;

    return GATEWAY_OK;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <cstring>
#include <span>
#include <expected>
#include <array>
#include <string_view>

namespace security::boundary {

inline constexpr uint16_t kMagic = 0x5345;
inline constexpr uint16_t kVersion = 1;
inline constexpr size_t kMaxPayload = 4096;

enum class GatewayError : uint16_t {
    Ok = 0,
    BadMagic,
    UnsupportedVersion,
    PayloadTooLarge,
    ChecksumMismatch,
    SchemaViolation,
    CanonicalizationFail,
    AccessDenied
};

#pragma pack(push, 1)
struct FrameHeader {
    uint16_t magic{kMagic};
    uint16_t version{kVersion};
    uint16_t opcode{0};
    uint16_t flags{0};
    uint32_t sequence_id{0};
    uint32_t payload_len{0};
};
#pragma pack(pop)

struct ValidatedMessage {
    FrameHeader header{};
    std::array<uint8_t, kMaxPayload> payload{};
    uint32_t checksum{0};
};

class [[nodiscard]] BoundaryValidator {
public:
    static std::expected<ValidatedMessage, GatewayError> validate(std::span<const uint8_t> raw_data) noexcept {
        if (raw_data.size() < sizeof(FrameHeader) + sizeof(uint32_t)) {
            return std::unexpected(GatewayError::SchemaViolation);
        }

        // Атомарне зчитування заголовка
        FrameHeader hdr{};
        std::memcpy(&hdr, raw_data.data(), sizeof(FrameHeader));

        if (hdr.magic != kMagic) {
            return std::unexpected(GatewayError::BadMagic);
        }
        if (hdr.version != kVersion) {
            return std::unexpected(GatewayError::UnsupportedVersion);
        }
        if (hdr.payload_len > kMaxPayload) {
            return std::unexpected(GatewayError::PayloadTooLarge);
        }

        const size_t total_size = sizeof(FrameHeader) + hdr.payload_len + sizeof(uint32_t);
        if (raw_data.size() < total_size) {
            return std::unexpected(GatewayError::SchemaViolation);
        }

        // Перевірка контрольної суми
        const uint32_t computed_crc = calculate_crc32(raw_data.subspan(0, sizeof(FrameHeader) + hdr.payload_len));
        uint32_t packet_crc{0};
        std::memcpy(&packet_crc, raw_data.data() + sizeof(FrameHeader) + hdr.payload_len, sizeof(uint32_t));

        if (computed_crc != packet_crc) {
            return std::unexpected(GatewayError::ChecksumMismatch);
        }

        ValidatedMessage msg{};
        msg.header = hdr;
        std::memcpy(msg.payload.data(), raw_data.data() + sizeof(FrameHeader), hdr.payload_len);
        msg.checksum = packet_crc;

        return msg;
    }

private:
    static uint32_t calculate_crc32(std::span<const uint8_t> data) noexcept {
        uint32_t crc = 0xFFFFFFFF;
        for (uint8_t byte : data) {
            crc ^= byte;
            for (int i = 0; i < 8; ++i) {
                crc = (crc >> 1) ^ (0xEDB88320 & (-(crc & 1)));
            }
        }
        return ~crc;
    }
};

} // namespace security::boundary
```
:::

## Правила поширення помилок через межу (Error Propagation)

Під час повернення результатів із довіреного контуру у менш довірений контур діє суворе правило **санітизації повідомлень про помилки**:

1. **Заборона розкриття внутрішньої структури (Information Disclosure):** Відповідь клієнту ніколи не повинна містити дампи пам'яті, трасування стека (Stack Traces), абсолютні шляхи до системних файлів або версії внутрішніх бібліотек. Порушення цього правила перетворює обробник помилок на оракул для зловмисника.
2. **Константний час відповіді (Timing Defense):** Якщо запит відхиляється через помилку автентифікації чи невалідний токен, перевірка повинна виконуватися за константний час, щоб уникнути атак за часом (Timing Attacks) на розпізнавання існуючих користувачів або валідних префіксів ключів.
3. **Уніфіковані коди відповідей:** Детальні причини збою записуються виключно у внутрішній захищений журнал аудиту, тоді як зовнішньому клієнту повертається узагальнений код помилки `ERR_ACCESS_DENIED` або `ERR_SCHEMA_VIOLATION`.
4. **Запобігання витоку ресурсів (Resource Leak Prevention):** Будь-яка помилка на етапі валідації кадру повинна негайно звільняти всі тимчасово виділені ресурси (буфери, тимчасові дескриптори), щоб виключити атаки вичерпання дескрипторів або пам'яті через спам некоректними запитами.
