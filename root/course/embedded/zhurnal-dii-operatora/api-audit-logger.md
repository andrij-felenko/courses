# 📋 Програмний інтерфейс захищеного логера дій оператора

Програмний інтерфейс логера аудиту визначає контракт збереження, криптографічного зв'язування та верифікації команд оператора в енергонезалежній пам'яті автономного апарата. Цей інтерфейс відокремлює логіку обробки протоколів зв'язку (MAVLink, CAN, власні телеметричні кадри) від апаратного драйвера мікросхеми Flash-пам'яті та забезпечує гарантії цілісності записів при раптовому знеструмленні.

Бібліотека надає C-інтерфейс для прямої інтеграції в обробники команд польотних стеків (на базі FreeRTOS, Zephyr або bare-metal) та ідіоматичний C++-інтерфейс із гарантіями RAII, типізованими статусами помилок через `std::expected` та переглядачами буферів `std::span`.

## Заголовні файли та константи конфігурації

Інтерфейс спирається на фіксований розмір бінарного кадру (128 байтів), що відповідає половині стандартної сторінки програмування SPI Flash (256 байтів) і гарантує відсутність накладних витрат на динамічне вирівнювання:

:::tabs
```c
#ifndef AUDIT_LOGGER_API_H
#define AUDIT_LOGGER_API_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define AUDIT_RECORD_SIZE       128U
#define AUDIT_HASH_SIZE         32U   /* SHA-256 */
#define AUDIT_MAGIC_SYNC        0x41554454U /* 'AUDT' у Little-Endian */
#define AUDIT_SECTOR_MAGIC      0x53454354U /* 'SECT' у Little-Endian */
#define AUDIT_MAX_PAYLOAD_SIZE  32U

/* Статуси повернення функцій логера */
typedef enum {
    AUDIT_OK                    =  0,
    AUDIT_ERR_INVALID_PARAM     = -1,
    AUDIT_ERR_FLASH_IO          = -2,
    AUDIT_ERR_CHAIN_CORRUPTED   = -3,
    AUDIT_ERR_BUFFER_FULL       = -4,
    AUDIT_ERR_NOT_INITIALIZED   = -5,
    AUDIT_ERR_UNALIGNED_ADDR    = -6,
    AUDIT_ERR_POWER_LOSS_DETECT = -7
} audit_status_t;

/* Статус виконання зафіксованої команди */
typedef enum {
    AUDIT_EXEC_PENDING          = 0x00, /* Команду прийнято, очікує перевірки */
    AUDIT_EXEC_ACCEPTED         = 0x01, /* Пройшла перевірку прав та інтерлоків */
    AUDIT_EXEC_REJECTED_AUTH    = 0x02, /* Відхилено: недійсний ключ/підпис */
    AUDIT_EXEC_REJECTED_SAFETY  = 0x03, /* Відхилено: блокування безпеки (Interlock) */
    AUDIT_EXEC_SUCCESS          = 0x04, /* Успішно виконано автопілотом */
    AUDIT_EXEC_FAILED           = 0x05, /* Помилка під час виконання приводу */
    AUDIT_EXEC_TIMEOUT          = 0x06  /* Час очікування підтвердження вичерпано */
} audit_exec_status_t;

/* Прапорці атрибутів запису */
typedef enum {
    AUDIT_FLAG_NONE             = 0x00,
    AUDIT_FLAG_EMERGENCY        = 0x01, /* Аварійна дія (Emergency Disarm/RTL) */
    AUDIT_FLAG_SIGNATURE_VALID  = 0x02, /* Наземний підпис Ed25519 перевірено */
    AUDIT_FLAG_RESERVED_BIT2    = 0x04,
    AUDIT_FLAG_SYNC_RTC         = 0x08  /* Час UTC синхронізовано з GNSS PPS */
} audit_flags_t;
```
```cpp
#pragma once

#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <expected>
#include <string_view>

namespace embedded::audit {

inline constexpr size_t RecordSize = 128;
inline constexpr size_t HashSize = 32;
inline constexpr uint32_t MagicSync = 0x41554454;   // 'AUDT'
inline constexpr uint32_t SectorMagic = 0x53454354; // 'SECT'
inline constexpr size_t MaxPayloadSize = 32;

enum class Status : int32_t {
    Ok = 0,
    InvalidParam = -1,
    FlashIo = -2,
    ChainCorrupted = -3,
    BufferFull = -4,
    NotInitialized = -5,
    UnalignedAddr = -6,
    PowerLossDetected = -7
};

enum class ExecStatus : uint8_t {
    Pending = 0x00,
    Accepted = 0x01,
    RejectedAuth = 0x02,
    RejectedSafety = 0x03,
    Success = 0x04,
    Failed = 0x05,
    Timeout = 0x06
};

enum class RecordFlags : uint8_t {
    None = 0x00,
    Emergency = 0x01,
    SignatureValid = 0x02,
    SyncRtc = 0x08
};

inline constexpr RecordFlags operator|(RecordFlags a, RecordFlags b) noexcept {
    return static_cast<RecordFlags>(static_cast<uint8_t>(a) | static_cast<uint8_t>(b));
}

inline constexpr bool operator&(RecordFlags a, RecordFlags b) noexcept {
    return (static_cast<uint8_t>(a) & static_cast<uint8_t>(b)) != 0;
}

} // namespace embedded::audit
```
:::

## Опис кодів помилок та статусів

Коди помилок переліку `audit_status_t` мають чітку семантику для діагностики відмов підсистем:

- `AUDIT_OK` (0): Операція успішно завершена, стан пам'яті та криптографічний ланцюг узгоджені.
- `AUDIT_ERR_INVALID_PARAM` (-1): Передано нульовий покажчик, неприпустиму довжину корисного навантаження (понад 32 байти) або непідтримувану конфігурацію секторів Flash.
- `AUDIT_ERR_FLASH_IO` (-2): Апаратна помилка шини SPI/QSPI або відмова мікросхеми Flash-пам'яті під час виконання операцій читання, програмування сторінки чи стирання сектора.
- `AUDIT_ERR_CHAIN_CORRUPTED` (-3): Порушення криптографічної цілісності журналу. Розрахований хеш поточного кадру не збігається зі збереженим значенням або порушено посилання на хеш попереднього запису `prev_hash`.
- `AUDIT_ERR_BUFFER_FULL` (-4): Усі виділені сектори заповнені, а ротація заблокована прапорцем захисту від перезапису важливих аварійних сесій.
- `AUDIT_ERR_NOT_INITIALIZED` (-5): Спроба виклику функцій запису або верифікації до успішного завершення процедури `audit_logger_init()`.
- `AUDIT_ERR_UNALIGNED_ADDR` (-6): Передана фізична адреса буфера або зміщення у Flash не вирівняні за межею 128 байтів.
- `AUDIT_ERR_POWER_LOSS_DETECT` (-7): Під час ініціалізації виявлено незавершений запис кадру внаслідок раптового знеструмлення; виконано відкат до останнього валідного слота.

## Структури бінарного формату

Кожен бінарний кадр `audit_record_t` упаковано з жорстким вирівнюванням полів за 4- та 8-байтовими межами для запобігання апаратних виключень на ядрах ARM Cortex-M:

:::tabs
```c
#pragma pack(push, 1)

/* Структура одного запису аудиту (рівно 128 байтів) */
typedef struct {
    uint32_t magic;                     /* 0..3:   0x41554454 ('AUDT') */
    uint8_t  version;                   /* 4:      Версія формату (0x01) */
    uint8_t  flags;                     /* 5:      Бітова маска audit_flags_t */
    uint8_t  exec_status;               /* 6:      audit_exec_status_t */
    uint8_t  payload_len;               /* 7:      Довжина валідних байтів у payload */
    uint64_t sequence_id;               /* 8..15:  Монотонний лічильник записів */
    uint64_t timestamp_utc_ms;          /* 16..23: Unix Epoch у мілісекундах */
    uint64_t operator_id;               /* 24..31: Ідентифікатор оператора / хеш ключа */
    uint16_t command_id;                /* 32..33: Код команди (MAVLink або custom) */
    uint8_t  subsystem_id;              /* 34:     Цільовий вузол (Autopilot, Gimbal) */
    uint8_t  padding0;                  /* 35:     Вирівнювання */
    uint8_t  payload[AUDIT_MAX_PAYLOAD_SIZE]; /* 36..67: Аргументи команди */
    uint8_t  prev_hash[AUDIT_HASH_SIZE];      /* 68..99: SHA-256 попереднього кадру */
    uint8_t  record_hash[AUDIT_HASH_SIZE];    /* 100..127: SHA-256 поточного кадру */
} audit_record_t;

/* Заголовок 4-кілобайтного сектора Flash */
typedef struct {
    uint32_t sector_magic;              /* 0..3:   0x53454354 ('SECT') */
    uint32_t sector_index;              /* 4..7:   Порядковий номер сектора */
    uint64_t base_sequence_id;          /* 8..15:  Sequence ID першого запису */
    uint8_t  start_hash[AUDIT_HASH_SIZE];/* 16..47: Вхідний хеш ланцюга сектора */
    uint32_t records_count;             /* 48..51: Загальна кількість записів (0xFFFFFFFF якщо пишеться) */
    uint8_t  end_hash[AUDIT_HASH_SIZE]; /* 52..83: Фінальний хеш сектора (при закритті) */
    uint8_t  reserved[44];              /* 84..127: Доповнення до 128 байтів */
} audit_sector_header_t;

#pragma pack(pop)
```
```cpp
namespace embedded::audit {

#pragma pack(push, 1)

struct Record {
    uint32_t magic{MagicSync};
    uint8_t  version{1};
    uint8_t  flags{0};
    uint8_t  exec_status{static_cast<uint8_t>(ExecStatus::Pending)};
    uint8_t  payload_len{0};
    uint64_t sequence_id{0};
    uint64_t timestamp_utc_ms{0};
    uint64_t operator_id{0};
    uint16_t command_id{0};
    uint8_t  subsystem_id{0};
    uint8_t  padding0{0};
    std::array<uint8_t, MaxPayloadSize> payload{};
    std::array<uint8_t, HashSize> prev_hash{};
    std::array<uint8_t, HashSize> record_hash{};
};
static_assert(sizeof(Record) == RecordSize, "Record struct size must be exactly 128 bytes");

struct SectorHeader {
    uint32_t sector_magic{SectorMagic};
    uint32_t sector_index{0};
    uint64_t base_sequence_id{0};
    std::array<uint8_t, HashSize> start_hash{};
    uint32_t records_count{0xFFFFFFFF};
    std::array<uint8_t, HashSize> end_hash{};
    std::array<uint8_t, 44> reserved{};
};
static_assert(sizeof(SectorHeader) == RecordSize, "SectorHeader struct size must be exactly 128 bytes");

#pragma pack(pop)

} // namespace embedded::audit
```
:::

## Семантика полів запису

1. `magic`: Постійне значення `0x41554454` (символи 'A', 'U', 'D', 'T'). Використовується сканером для розпізнавання ініціалізованого слота від стертої області пам'яті (`0xFFFFFFFF`).
2. `sequence_id`: 64-розрядний монотонно зростаючий лічильник. Гарантує унікальність і суворий порядок транзакцій, унеможливлюючи атаки повторного відтворення (Replay Attack).
3. `timestamp_utc_ms`: Час отримання наказу в мілісекундах від початку епохи Unix. Формується на основі даних супутникової навігації GNSS та локального годинника RTC.
4. `operator_id`: 64-розрядний числовий ідентифікатор оператора. У криптографічних схемах сюди поміщається усічений до 8 байтів SHA-256 хеш відкритого ключа оператора, яким підписано сесію керування.
5. `command_id`: Ідентифікатор наказу. Для сумісності з автопілотами на базі MAVLink відповідає значенням `MAV_CMD` (наприклад, 21 для `MAV_CMD_NAV_LAND`, 400 для `MAV_CMD_COMPONENT_ARM_DISARM`).
6. `payload`: Фіксований буфер розміром 32 байти. Зберігає числові аргументи команди (цільова висота, широта, довгота, швидкість, бітова маска моторів).
7. `prev_hash`: 32 байти дайджесту SHA-256 безпосередньо попереднього запису. Забезпечує криптографічну зв'язність ланцюга.
8. `record_hash`: 32 байти дайджесту SHA-256 від перших 96 байтів поточного кадру (включно з полем `prev_hash`).

## Апаратний драйверний інтерфейс Flash (HAL)

Логер не здійснює прямих звернень до регістрів мікроконтролера, а делегує читання, запис та стирання секторів через таблицю функцій (C) або абстрактний клас інтерфейсу (C++):

:::tabs
```c
/* Таблиця операцій апаратного драйвера енергонезалежної пам'яті */
typedef struct {
    /* Читання блоку даних з фізичної адреси */
    audit_status_t (*read)(uint32_t physical_addr, uint8_t *buf, size_t len);
    
    /* Запис сторінки Flash (розмір сторінки зазвичай 256 байтів, вирівняно) */
    audit_status_t (*write_page)(uint32_t physical_addr, const uint8_t *buf, size_t len);
    
    /* Стирання одного сектора Flash (зазвичай 4096 байтів) */
    audit_status_t (*erase_sector)(uint32_t sector_addr);
    
    /* Загальний розмір виділеної області пам'яті під аудит (у байтах) */
    uint32_t total_size_bytes;
    
    /* Розмір одного фізичного сектора (наприклад, 4096) */
    uint32_t sector_size_bytes;
} audit_flash_hal_t;
```
```cpp
namespace embedded::audit {

class IFlashStorage {
public:
    virtual ~IFlashStorage() = default;
    virtual std::expected<void, Status> read(uint32_t physical_addr, std::span<uint8_t> dst) noexcept = 0;
    virtual std::expected<void, Status> write_page(uint32_t physical_addr, std::span<const uint8_t> src) noexcept = 0;
    virtual std::expected<void, Status> erase_sector(uint32_t sector_addr) noexcept = 0;
    [[nodiscard]] virtual uint32_t total_size() const noexcept = 0;
    [[nodiscard]] virtual uint32_t sector_size() const noexcept = 0;
};

} // namespace embedded::audit
```
:::

### Вимоги до реалізації апаратного драйвера

1. **Блокування та тайм-аути:** Функція `write_page` повинна чекати скидання біта `WIP` (Write In Progress) у регістрі стану Flash або повертати помилку `AUDIT_ERR_FLASH_IO` за таймаутом (зазвичай не більше ніж 5 мс для запису сторінки та 100 мс для стирання сектора).
2. **Атомарність викликів:** Драйвер повинен забезпечувати монопольний доступ до шини SPI через апаратні м'ютекси RTOS або критичні секції при роботі в багатозадачному середовищі.
3. **Кешування шини:** При роботі на мікроконтролерах із процесорним кешем даних (D-Cache на Cortex-M7) буфери, що передаються у драйвер через DMA, повинні бути вирівняні за межею рядка кешу (32 байти) та пройти операцію валідації/інвалідації кешу (Cache Clean/Invalidate) до та після передачі.

## Функції життєвого циклу логера

Контракт викликів охоплює ініціалізацію зі скануванням існуючих секторів, додавання команди з автоматичним обчисленням SHA-256, оновлення статусу виконання та верифікацію криптографічного ланцюга:

:::tabs
```c
/* Структура дескриптора контексту логера аудиту */
typedef struct {
    const audit_flash_hal_t *hal;
    uint64_t current_seq_id;
    uint32_t active_sector_idx;
    uint32_t next_slot_offset;
    uint8_t  last_hash[AUDIT_HASH_SIZE];
    bool     initialized;
} audit_context_t;

/*
 * audit_logger_init:
 *   Ініціалізує контекст, сканує Flash-пам'ять, знаходить активний сектор,
 *   відновлює Sequence ID та останній валідний хеш ланцюга.
 */
audit_status_t audit_logger_init(audit_context_t *ctx, const audit_flash_hal_t *hal);

/*
 * audit_logger_record_command:
 *   Формує новий запис аудиту, прив'язує його до попереднього хешу,
 *   обчислює SHA-256 і атомарно записує кадр у відкритий слот Flash.
 */
audit_status_t audit_logger_record_command(
    audit_context_t *ctx,
    uint64_t timestamp_utc_ms,
    uint64_t operator_id,
    uint16_t command_id,
    uint8_t subsystem_id,
    audit_flags_t flags,
    const uint8_t *payload,
    uint8_t payload_len,
    uint64_t *out_seq_id
);

/*
 * audit_logger_update_ack:
 *   Фіксує результат виконання раніше зареєстрованої команди (ACK).
 */
audit_status_t audit_logger_update_ack(
    audit_context_t *ctx,
    uint64_t target_seq_id,
    uint64_t timestamp_utc_ms,
    audit_exec_status_t exec_status,
    uint32_t error_code
);

/*
 * audit_logger_verify_chain:
 *   Зчитує всі записи від TAIL до HEAD та перевіряє неперервність ланцюга SHA-256.
 *   Повертає AUDIT_OK якщо підробок немає, або AUDIT_ERR_CHAIN_CORRUPTED із
 *   номером скомпрометованого запису в out_corrupted_seq.
 */
audit_status_t audit_logger_verify_chain(
    const audit_context_t *ctx,
    uint64_t *out_corrupted_seq
);
```
```cpp
namespace embedded::audit {

class AuditLogger {
public:
    explicit AuditLogger(IFlashStorage& storage) noexcept;
    ~AuditLogger() = default;

    AuditLogger(const AuditLogger&) = delete;
    AuditLogger& operator=(const AuditLogger&) = delete;
    AuditLogger(AuditLogger&&) noexcept = default;
    AuditLogger& operator=(AuditLogger&&) noexcept = default;

    [[nodiscard]] std::expected<void, Status> init() noexcept;

    [[nodiscard]] std::expected<uint64_t, Status> record_command(
        uint64_t timestamp_utc_ms,
        uint64_t operator_id,
        uint16_t command_id,
        uint8_t subsystem_id,
        RecordFlags flags,
        std::span<const uint8_t> payload
    ) noexcept;

    [[nodiscard]] std::expected<void, Status> update_ack(
        uint64_t target_seq_id,
        uint64_t timestamp_utc_ms,
        ExecStatus exec_status,
        uint32_t error_code
    ) noexcept;

    [[nodiscard]] std::expected<void, uint64_t> verify_chain() const noexcept;

    [[nodiscard]] uint64_t current_sequence_id() const noexcept { return current_seq_id_; }
    [[nodiscard]] std::span<const uint8_t, HashSize> latest_hash() const noexcept { return last_hash_; }

private:
    IFlashStorage& storage_;
    uint64_t current_seq_id_{0};
    uint32_t active_sector_idx_{0};
    uint32_t next_slot_offset_{0};
    std::array<uint8_t, HashSize> last_hash_{};
    bool initialized_{false};

    std::expected<void, Status> scan_sectors() noexcept;
    std::expected<void, Status> rotate_sector() noexcept;
};

} // namespace embedded::audit
```
:::

## Інваріанти роботи та гарантії цілісності

1. **Монотонність sequence_id:** Кожен новий запис отримує номер `N = N_prev + 1`. Спроба записати кадр із порушенням монотонності відхиляється на рівні верифікатора.
2. **Незмінність історичних слотів:** Запис здійснюється виключно в чисті комірки (`0xFF`). Повторний запис у вже заповнений слот без попереднього стирання сектора апаратно заборонений.
3. **Атомарність коміту:** Кадр стає валідним лише після запису байтів магічного числа `AUDIT_MAGIC_SYNC` та відповідного хешу `record_hash`. Якщо живлення зникає під час запису байтів корисного навантаження, при наступному старті сканер виявить незавершений запис за нульовим або пошкодженим хешем і виконає відновлення останнього стабільного стану ланцюга.
4. **Конкурентність та безпека переривань:** Виклик `audit_logger_record_command()` є безпечним для виклику з контексту задач RTOS за умови використання внутрішнього блокування. Прямий виклик функцій запису у Flash із контексту апаратних переривань (ISR) заборонений через блокуючий характер транзакцій шини SPI; для таких випадків формується черга подій у швидкій SRAM з подальшим скиданням фоновою задачею логера.
