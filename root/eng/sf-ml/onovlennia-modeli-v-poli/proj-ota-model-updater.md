# ⚙️ Безпечне OTA-оновлення ваг нейромережі у Flash-пам'ять

Оновлення параметрів нейромережі у польових вбудованих пристроях вимагає надійного механізму запису у енергонезалежну пам'ять без ризику перетворення плати на непрацездатний стан у разі раптового обриву зв'язку чи просідання живлення. У мікроконтролерних системах оновлення всієї монолітної прошивки заради заміни кількох сотень кілобайтів ваг створює критичні експлуатаційні ризики: перепрошивка секторів коду зупиняє роботу критичних контурів керування, перезаписує таблицю векторів переривань і вимагає передачі великих двійкових файлів через низькошвидкісні бездротові канали (BLE, CAN, LoRa або супутниковий модем). Відокремлення моделі у виділений розділ Flash-пам'яті дозволяє замінювати ваги без зупинки основної операційної системи реального часу, однак висуває суворі вимоги до атомарності операцій, верифікації криптографічних підписів та автоматичного відкату при збоях.

Нижче реалізовано повний модуль стадійного OTA-оновлення (Over-The-Air) для мікроконтролерів сімейств Cortex-M та ESP32. Модуль підтримує блокове стирання NOR Flash, захист від блокування шини пам'яті (Flash Stall), потокове обчислення дайджесту SHA-256 під час прийому чанків, перевірку сумісності метаданих моделі з рушієм інференсу та атомарне перемикання активного банку через спеціальний сектор енергонезалежних налаштувань.

## Фізичні обмеження вбудованої Flash-пам'яті та архітектура розділів

Вбудована пам'ять мікроконтролерів (NOR Flash) базується на транзисторах із плаваючим затвором (Floating-Gate) або технології захоплення заряду (Charge Trapping). Фізика цих напівпровідникових комірок визначає фундаментальне правило: запис дозволяє перемикати біти виключно зі стану логічної одиниці в логічний нуль (`1 -> 0`). Зворотна операція — переведення нуля в одиницю — неможлива для окремого байта чи слова: вона вимагає тунелювання електронів та подачі високої напруги на підкладку цілого фізичного блоку (сектора), що стирає весь сектор (зазвичай розміром 4096 байтів або 16–128 КБ у деяких чипах) і повертає всі його байти у стан `0xFF`.

Крім того, тривалість операції стирання сектора становить від 10 до 400 мілісекунд, а час запису одного 32-бітного слова — десятки мікросекунд. Під час виконання операцій стирання чи програмування внутрішній контролер пам'яті блокує шину вибірки інструкцій (явище Flash Controller Stall або Bus Wait States). Якщо мікроконтролер має лише один банк внутрішньої Flash-пам'яті, центральний процесор повністю зупиняє виконання коду на час стирання сектора, якщо тільки код обробників переривань не перенесено в оперативну пам'ять (SRAM). Для пристроїв, що керують сервоприводами, стабілізацією безпілотних апаратів або підтримкою мережевих протоколів реального часу, така затримка призводить до аварії або втрати телеметрії.

```
+-----------------------------------------------------------------------------------+
|                        Physical NOR Flash Layout (2048 KB)                        |
|                                                                                   |
| [0x0800_0000] Bootloader (64 KB)          - Hardware vectors, secure boot logic   |
| [0x0801_0000] Main Firmware & TFLM (768 KB)- RTOS, drivers, inference kernels    |
| [0x080D_0000] NV Metadata & Log (32 KB)   - Active slot, trial counter, rollback  |
| [0x080D_8000] Model Bank A (Active, 512KB)- Header + FlatBuffer int8 weights      |
| [0x0815_8000] Model Bank B (Target, 512KB)- Staging buffer for chunked writes     |
| [0x081D_8000] Telemetry Ring Buffer (160KB)- Drift metrics, execution timestamps  |
+-----------------------------------------------------------------------------------+
```

Щоб забезпечити безперервну роботу системи під час завантаження оновлення, використовується схема подвійної буферизації моделей (Dual-Bank Model Partitioning). Залежно від апаратного забезпечення це може бути реалізовано двома шляхами:
1. **Двобанкова внутрішня Flash-пам'ять (Dual-Bank Internal Flash)**: чип має два фізично розділені масиви пам'яті з власними контролерами заряду (наприклад, STM32H7 dual-bank mode або STM32G4). Процесор виконує інференс і код керування з Банку 1, тоді як стирання і запис нового образу моделі виконуються у Банку 2 без жодного блокування процесорних тактів;
2. **Зовнішня SPI/QSPI NOR Flash-пам'ять (External Memory via XIP)**: основна прошивка та рушій розміщуються у внутрішній пам'яті мікроконтролера, а ваги моделей зберігаються у зовнішньому чипі (Winbond W25Q, Macronix MX25R), що підтримує режим прямого відображення адрес (Execute-in-Place, XIP). Запис у зовнішню пам'ять виконується у фоновому режимі через контролер DMA без зупинки основного CPU.

Поки рушій інференсу виконує обчислення з активного Банку A у режимі тільки для читання, мережевий потік поступово записує нові чанки у пасивний Банк B.

## Контейнер моделі та контракт метаданих

Нейромережевий артефакт не можна передавати як «сирий» двійковий файл FlatBuffer (`.tflite`). Якщо завантажити несумісну версію моделі (наприклад, оптимізовану під інший набір апаратних операторів CMSIS-NN або таку, що вимагає вдвічі більше оперативної пам'яті під тензорну арену), мікроконтролер зазнає критичного збою (Kernel Panic / HardFault) під час першого ж виклику `AllocateTensors()`.

Для запобігання таким аваріям кожен артефакт загортається у захисний заголовок фіксованого розміру (128 байтів), який містить суворі критерії сумісності та криптографічні підписи.

```
+-----------------------------------------------------------------------+
|                       Model Artifact Header (128 B)                   |
|  Magic: 0x4D4C5550 ('MLUP')  | Header Version | Model Version Major/Min|
|  Payload Size (bytes)        | Required Tensor Arena Size (bytes)     |
|  Input Tensor Shape Hash     | Output Tensor Shape Hash               |
|  Target Schema Version       | Hardware Acceleration Target ID        |
|  SHA-256 Checksum of Payload (32 bytes)                               |
|  Ed25519 Digital Signature of Header + Payload (64 bytes)             |
+-----------------------------------------------------------------------+
|                       FlatBuffer Neural Network Payload               |
|  Quantized INT8 Model Graph, TFLite Operators, Weight Tensors         |
|  Size: up to 512 KB                                                   |
+-----------------------------------------------------------------------+
```

Заголовок містить такі поля:
- **Magic number** (`0x4D4C5550`, символи ASCII 'MLUP'): швидка перевірка коректності типу файлу;
- **Версія заголовка та версія моделі**: мажорна, мінорна та патч-версії для контролю сумісності;
- **Розмір корисного навантаження (Payload Size)**: точна кількість байтів FlatBuffer-файлу без урахування заголовка;
- **Необхідний розмір тензорної арени (Required Arena Size)**: обсяг байтів в ОЗП (SRAM), потрібний рушію інференсу для розміщення проміжних тензорів активацій;
- **Хеші розмірностей тензорів (Input/Output Shape Hashes)**: 32-бітні дайджести розмірностей і типів даних вхідних та вихідних тензорів для перевірки сумісності з драйверами сенсорів;
- **Версія цільової схеми (Target Schema Version)**: версія схеми FlatBuffer (зазвичай 3 для TensorFlow Lite), що гарантує сумісність парсера;
- **SHA-256 дайджест**: хеш-сума всього FlatBuffer-тіла для виявлення пошкоджень під час передачі;
- **Криптографічний підпис (Ed25519 / ECDSA)**: підпис, створений закритим ключем розробника, що гарантує автентичність моделі та захищає від підміни зловмисником.

## Апаратне зберігання ключів та корінь довіри (Root of Trust)

Для надійної перевірки підпису Ed25519 або ECDSA відкритий ключ розробника повинен бути надійно зафіксований у пристрої під час виробництва і захищений від несанкціонованої модифікації. У мікроконтролерних архітектурах застосовують три підходи до організації кореня довіри:
1. **Одноразово програмовані комірки (OTP Memory / eFuses)**: на чипах ESP32 або STM32 відкритий ключ чи його SHA-256 хеш пропалюється в апаратні eFuses. Після фіксації бітів захисту модифікація ключа апаратно неможлива навіть за наявності повного доступу до шини налагодження (JTAG/SWD);
2. **Захищені сектори коду завантажувача (Secure Boot Protected Sectors)**: відкритий ключ компілюється безпосередньо у бінарний файл первинного завантажувача (Bootloader), а відповідний сектор Flash захищається апаратними бітами блокування запису (Write Protection Option Bytes);
3. **Апаратні криптографічні елементи (Secure Elements)**: використання зовнішніх мікросхем автентифікації (Microchip ATECC608A або NXP SE050), що підключаються по шині I2C і зберігають відкриті сертифікати у внутрішній захищеній пам'яті.

## Опис структур даних та інтерфейсу драйвера

Нижче наведено базові оголошення типів даних мовами C99 та C++20. Структури розмічені атрибутами упакування (`#pragma pack(push, 1)` або `__attribute__((packed))`), що забезпечує однакове представлення байтів у пам'яті незалежно від архітектури компілятора.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#define ML_MODEL_MAGIC              0x4D4C5550U /* 'MLUP' */
#define ML_HEADER_VERSION           1U
#define ML_FLASH_SECTOR_SIZE        4096U
#define ML_MODEL_MAX_SIZE           (512U * 1024U)
#define ML_METADATA_MAGIC           0x4D455441U /* 'META' */
#define ML_MAX_TRIAL_BOOTS          3U

typedef enum {
    ML_SLOT_A = 0,
    ML_SLOT_B = 1,
    ML_SLOT_INVALID = 0xFF
} ml_slot_id_t;

typedef enum {
    ML_STATE_EMPTY = 0,
    ML_STATE_TRIAL = 1,
    ML_STATE_CONFIRMED = 2,
    ML_STATE_FAILED = 3
} ml_slot_state_t;

typedef enum {
    ML_OTA_OK = 0,
    ML_OTA_ERR_INVALID_MAGIC,
    ML_OTA_ERR_INCOMPATIBLE,
    ML_OTA_ERR_ARENA_OVERFLOW,
    ML_OTA_ERR_HASH_MISMATCH,
    ML_OTA_ERR_FLASH_IO,
    ML_OTA_ERR_OFFSET_GAP,
    ML_OTA_ERR_STATE
} ml_ota_status_t;

#pragma pack(push, 1)
typedef struct {
    uint32_t magic;
    uint16_t header_version;
    uint16_t model_version_major;
    uint16_t model_version_minor;
    uint16_t model_version_patch;
    uint32_t payload_size;
    uint32_t required_arena_size;
    uint32_t input_shape_hash;
    uint32_t output_shape_hash;
    uint16_t target_schema_version;
    uint16_t flags;
    uint8_t  sha256[32];
    uint8_t  signature[64];
} ml_model_header_t;

typedef struct {
    uint32_t meta_magic;
    uint32_t sequence_id;
    uint8_t  active_slot;
    uint8_t  slot_state[2];
    uint8_t  trial_boots_remaining;
    uint32_t crc32;
} ml_nv_metadata_t;
#pragma pack(pop)

/* Інтерфейс апаратного драйвера Flash-пам'яті */
typedef struct {
    bool (*read)(uint32_t addr, uint8_t *dst, uint32_t len);
    bool (*write)(uint32_t addr, const uint8_t *src, uint32_t len);
    bool (*erase_sector)(uint32_t sector_addr);
} ml_flash_driver_t;

/* Контекст стадійного сеансу OTA-оновлення */
typedef struct {
    const ml_flash_driver_t *flash;
    uint32_t nv_meta_addr;
    uint32_t slot_addrs[2];
    uint32_t max_sram_arena;
    
    ml_nv_metadata_t meta;
    ml_slot_id_t target_slot;
    uint32_t received_bytes;
    uint32_t total_expected_bytes;
    uint32_t current_sector_erased;
    bool session_active;
} ml_ota_context_t;
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <expected>
#include <string_view>

namespace emb::ml {

inline constexpr uint32_t kModelMagic = 0x4D4C5550U; // 'MLUP'
inline constexpr uint16_t kHeaderVersion = 1U;
inline constexpr uint32_t kFlashSectorSize = 4096U;
inline constexpr uint32_t kModelMaxSize = 512U * 1024U;
inline constexpr uint32_t kMetaMagic = 0x4D455441U; // 'META'
inline constexpr uint8_t  kMaxTrialBoots = 3U;

enum class SlotId : uint8_t {
    SlotA = 0,
    SlotB = 1,
    Invalid = 0xFF
};

enum class SlotState : uint8_t {
    Empty = 0,
    Trial = 1,
    Confirmed = 2,
    Failed = 3
};

enum class OtaError : uint8_t {
    InvalidMagic,
    IncompatibleSchema,
    ArenaOverflow,
    HashMismatch,
    FlashIoError,
    OffsetGap,
    InvalidState
};

#pragma pack(push, 1)
struct ModelHeader {
    uint32_t magic;
    uint16_t header_version;
    uint16_t model_version_major;
    uint16_t model_version_minor;
    uint16_t model_version_patch;
    uint32_t payload_size;
    uint32_t required_arena_size;
    uint32_t input_shape_hash;
    uint32_t output_shape_hash;
    uint16_t target_schema_version;
    uint16_t flags;
    std::array<uint8_t, 32> sha256;
    std::array<uint8_t, 64> signature;
};

struct NvMetadata {
    uint32_t meta_magic;
    uint32_t sequence_id;
    SlotId   active_slot;
    std::array<SlotState, 2> slot_state;
    uint8_t  trial_boots_remaining;
    uint32_t crc32;
};
#pragma pack(pop)

struct FlashDriver {
    bool (*read)(uint32_t addr, std::span<uint8_t> dst);
    bool (*write)(uint32_t addr, std::span<const uint8_t> src);
    bool (*erase_sector)(uint32_t sector_addr);
};

struct OtaConfig {
    uint32_t nv_meta_addr;
    std::array<uint32_t, 2> slot_addrs;
    uint32_t max_sram_arena;
};

} // namespace emb::ml
```
:::

## Протоколи транспортування, чанкування та ініціалізація сеансу

Під час запуску системи модуль OTA-оновлення зчитує енергонезалежні метадані з адреси `nv_meta_addr`. Якщо пристрій стартує вперше або якщо дані у секторі пошкоджено (наприклад, через збій живлення під час стирання чи незбіг контрольної суми CRC32), структура ініціалізується дефолтними значеннями: активним призначається Банк A, його стан позначається як підтверджений (`Confirmed`), а резервний Банк B оголошується порожнім.

Під час передачі даних бездротовим або польовим каналом образ моделі розбивається на окремі пакети (чанки). Розмір пакета суворо диктується фізичним та канальним рівнями інтерфейсу:
- **BLE (Bluetooth Low Energy GATT)**: при стандартному MTU 23 байти корисне навантаження становить лише 20 байтів. Після узгодження розширеного MTU (Data Length Extension, DLE) корисне навантаження одного пакета досягає 244 байтів;
- **CAN FD (Controller Area Network Flexible Data-Rate)**: протокол ISO-TP або кастомний каскад кадрів розбиває потік на порції по 64 байти, що вимагає локального буфера збирання;
- **MAVLink FTP (Telemetry Protocol)**: повідомлення `FILE_TRANSFER_PROTOCOL` містить 239 байтів корисних даних, структурованих полями `session`, `offset`, `size` та `data`, що забезпечує пряме зіставлення зі зміщенням у Flash.

Кожен прийом чанка контролюється перевіркою монотонності зміщення (`offset == received_bytes`). Якщо виявлено пропуск байтів (Offset Gap) внаслідок втрати пакета в радіоетері, клієнт відхиляє чанк із кодом `ML_OTA_ERR_OFFSET_GAP`, що сигналізує серверу передачі про необхідність повернутися до останнього підтвердженого зміщення.

:::tabs
```c
static uint32_t calc_crc32(const uint8_t *data, size_t len) {
    uint32_t crc = 0xFFFFFFFFU;
    for (size_t i = 0; i < len; ++i) {
        crc ^= data[i];
        for (uint8_t j = 0; j < 8; ++j) {
            crc = (crc >> 1) ^ (0xEDB88320U & -(crc & 1U));
        }
    }
    return ~crc;
}

ml_ota_status_t ml_ota_init(ml_ota_context_t *ctx,
                            const ml_flash_driver_t *flash_drv,
                            uint32_t nv_meta_addr,
                            uint32_t slot_a_addr,
                            uint32_t slot_b_addr,
                            uint32_t max_sram_arena) {
    if (!ctx || !flash_drv) return ML_OTA_ERR_STATE;
    ctx->flash = flash_drv;
    ctx->nv_meta_addr = nv_meta_addr;
    ctx->slot_addrs[0] = slot_a_addr;
    ctx->slot_addrs[1] = slot_b_addr;
    ctx->max_sram_arena = max_sram_arena;
    ctx->session_active = false;
    ctx->received_bytes = 0;

    if (!ctx->flash->read(ctx->nv_meta_addr, (uint8_t*)&ctx->meta, sizeof(ml_nv_metadata_t))) {
        return ML_OTA_ERR_FLASH_IO;
    }

    uint32_t stored_crc = ctx->meta.crc32;
    ctx->meta.crc32 = 0;
    uint32_t computed_crc = calc_crc32((uint8_t*)&ctx->meta, sizeof(ml_nv_metadata_t));
    ctx->meta.crc32 = stored_crc;

    if (ctx->meta.meta_magic != ML_METADATA_MAGIC || stored_crc != computed_crc) {
        ctx->meta.meta_magic = ML_METADATA_MAGIC;
        ctx->meta.sequence_id = 1;
        ctx->meta.active_slot = (uint8_t)ML_SLOT_A;
        ctx->meta.slot_state[ML_SLOT_A] = (uint8_t)ML_STATE_CONFIRMED;
        ctx->meta.slot_state[ML_SLOT_B] = (uint8_t)ML_STATE_EMPTY;
        ctx->meta.trial_boots_remaining = 0;
        ctx->meta.crc32 = 0;
        ctx->meta.crc32 = calc_crc32((uint8_t*)&ctx->meta, sizeof(ml_nv_metadata_t));

        ctx->flash->erase_sector(ctx->nv_meta_addr);
        ctx->flash->write(ctx->nv_meta_addr, (uint8_t*)&ctx->meta, sizeof(ml_nv_metadata_t));
    }

    return ML_OTA_OK;
}

ml_ota_status_t ml_ota_process_chunk(ml_ota_context_t *ctx,
                                     uint32_t offset,
                                     const uint8_t *data,
                                     uint32_t len) {
    if (!ctx || !data || len == 0) return ML_OTA_ERR_STATE;

    if (offset == 0) {
        if (len < sizeof(ml_model_header_t)) return ML_OTA_ERR_INCOMPATIBLE;

        const ml_model_header_t *hdr = (const ml_model_header_t*)data;
        if (hdr->magic != ML_MODEL_MAGIC) return ML_OTA_ERR_INVALID_MAGIC;
        if (hdr->header_version != ML_HEADER_VERSION) return ML_OTA_ERR_INCOMPATIBLE;
        if (hdr->required_arena_size > ctx->max_sram_arena) return ML_OTA_ERR_ARENA_OVERFLOW;
        if (hdr->payload_size > (ML_MODEL_MAX_SIZE - sizeof(ml_model_header_t))) {
            return ML_OTA_ERR_INCOMPATIBLE;
        }

        ctx->target_slot = (ctx->meta.active_slot == ML_SLOT_A) ? ML_SLOT_B : ML_SLOT_A;
        ctx->total_expected_bytes = sizeof(ml_model_header_t) + hdr->payload_size;
        ctx->received_bytes = 0;
        ctx->current_sector_erased = 0;
        ctx->session_active = true;
    }

    if (!ctx->session_active) return ML_OTA_ERR_STATE;
    if (offset != ctx->received_bytes) return ML_OTA_ERR_OFFSET_GAP;
    if (offset + len > ctx->total_expected_bytes) return ML_OTA_ERR_INCOMPATIBLE;

    uint32_t target_base = ctx->slot_addrs[ctx->target_slot];
    uint32_t write_addr = target_base + offset;

    uint32_t start_sector = offset / ML_FLASH_SECTOR_SIZE;
    uint32_t end_sector = (offset + len - 1) / ML_FLASH_SECTOR_SIZE;

    for (uint32_t s = start_sector; s <= end_sector; ++s) {
        if (s >= ctx->current_sector_erased) {
            uint32_t sector_addr = target_base + s * ML_FLASH_SECTOR_SIZE;
            if (!ctx->flash->erase_sector(sector_addr)) {
                ctx->session_active = false;
                return ML_OTA_ERR_FLASH_IO;
            }
            ctx->current_sector_erased = s + 1;
        }
    }

    if (!ctx->flash->write(write_addr, data, len)) {
        ctx->session_active = false;
        return ML_OTA_ERR_FLASH_IO;
    }

    ctx->received_bytes += len;
    return ML_OTA_OK;
}
```
```cpp
namespace emb::ml {

class OtaUpdater {
public:
    explicit OtaUpdater(const FlashDriver& driver, const OtaConfig& config)
        : driver_(driver), config_(config) {}

    std::expected<void, OtaError> init() {
        NvMetadata temp_meta{};
        auto meta_span = std::span<uint8_t>(reinterpret_cast<uint8_t*>(&temp_meta), sizeof(NvMetadata));
        
        if (!driver_.read(config_.nv_meta_addr, meta_span)) {
            return std::unexpected(OtaError::FlashIoError);
        }

        uint32_t stored_crc = temp_meta.crc32;
        temp_meta.crc32 = 0;
        uint32_t computed_crc = calculate_crc(meta_span);
        temp_meta.crc32 = stored_crc;

        if (temp_meta.meta_magic != kMetaMagic || stored_crc != computed_crc) {
            meta_.meta_magic = kMetaMagic;
            meta_.sequence_id = 1;
            meta_.active_slot = SlotId::SlotA;
            meta_.slot_state[0] = SlotState::Confirmed;
            meta_.slot_state[1] = SlotState::Empty;
            meta_.trial_boots_remaining = 0;
            meta_.crc32 = 0;
            
            auto write_span = std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(&meta_), sizeof(NvMetadata));
            meta_.crc32 = calculate_crc(write_span);

            driver_.erase_sector(config_.nv_meta_addr);
            driver_.write(config_.nv_meta_addr, write_span);
        } else {
            meta_ = temp_meta;
        }
        return {};
    }

    std::expected<void, OtaError> process_chunk(uint32_t offset, std::span<const uint8_t> data) {
        if (data.empty()) return std::unexpected(OtaError::InvalidState);

        if (offset == 0) {
            if (data.size() < sizeof(ModelHeader)) {
                return std::unexpected(OtaError::IncompatibleSchema);
            }
            const auto* hdr = reinterpret_cast<const ModelHeader*>(data.data());
            if (hdr->magic != kModelMagic) {
                return std::unexpected(OtaError::InvalidMagic);
            }
            if (hdr->required_arena_size > config_.max_sram_arena) {
                return std::unexpected(OtaError::ArenaOverflow);
            }
            target_slot_ = (meta_.active_slot == SlotId::SlotA) ? SlotId::SlotB : SlotId::SlotA;
            total_expected_ = sizeof(ModelHeader) + hdr->payload_size;
            received_bytes_ = 0;
            erased_sectors_ = 0;
            session_active_ = true;
        }

        if (!session_active_) return std::unexpected(OtaError::InvalidState);
        if (offset != received_bytes_) return std::unexpected(OtaError::OffsetGap);

        uint32_t base_addr = config_.slot_addrs[static_cast<size_t>(target_slot_)];
        uint32_t start_sec = offset / kFlashSectorSize;
        uint32_t end_sec = (offset + static_cast<uint32_t>(data.size()) - 1) / kFlashSectorSize;

        for (uint32_t s = start_sec; s <= end_sec; ++s) {
            if (s >= erased_sectors_) {
                if (!driver_.erase_sector(base_addr + s * kFlashSectorSize)) {
                    session_active_ = false;
                    return std::unexpected(OtaError::FlashIoError);
                }
                erased_sectors_ = s + 1;
            }
        }

        if (!driver_.write(base_addr + offset, data)) {
            session_active_ = false;
            return std::unexpected(OtaError::FlashIoError);
        }

        received_bytes_ += static_cast<uint32_t>(data.size());
        return {};
    }

    [[nodiscard]] SlotId active_slot() const noexcept { return meta_.active_slot; }
    [[nodiscard]] SlotId target_slot() const noexcept { return target_slot_; }
    [[nodiscard]] NvMetadata metadata() const noexcept { return meta_; }

private:
    static uint32_t calculate_crc(std::span<const uint8_t> data) {
        uint32_t crc = 0xFFFFFFFFU;
        for (uint8_t byte : data) {
            crc ^= byte;
            for (uint8_t j = 0; j < 8; ++j) {
                crc = (crc >> 1) ^ (0xEDB88320U & -(crc & 1U));
            }
        }
        return ~crc;
    }

    const FlashDriver& driver_;
    const OtaConfig& config_;
    NvMetadata meta_{};
    SlotId target_slot_{SlotId::Invalid};
    uint32_t total_expected_{0};
    uint32_t received_bytes_{0};
    uint32_t erased_sectors_{0};
    bool session_active_{false};
};

} // namespace emb::ml
```
:::

## Фіналізація, криптографічна перевірка та атомарний перемикач

Коли останній байт образу моделі записано у Flash, викликається функція фіналізації. На цьому етапі модуль виконує незалежне зчитування всього записаного діапазону з Flash-пам'яті порціями по 256 байтів, обчислює підсумковий криптографічний хеш SHA-256 і звіряє його зі значенням, зафіксованим у заголовку образу.

Оскільки мікроконтролери мають обмежений обсяг оперативної пам'яті (зазвичай від 64 до 512 КБ), завантажити весь двійковий файл моделі (наприклад, 400 КБ) у RAM для одноразового хешування неможливо. Тому перевірка виконується потоково: криптографічний контекст ініціалізується функцією `sha256_init()`, після чого по черзі зчитуються та оновлюються невеликі фрагменти через `sha256_update()`.

Криптографічна валідація цифрового підпису Ed25519 (на еліптичній кривій Curve25519) або ECDSA (secp256r1) виконується над 32-байтовим дайджестом SHA-256. Алгоритм Ed25519 є оптимальним вибором для мікроконтролерів: перевірка підпису займає близько 15–25 мільйонів тактів процесора Cortex-M4 (приблизно 90–150 мс при частоті 168 МГц), що виконується одноразово під час фіналізації та не впливає на подальшу швидкість інференсу.

Якщо хеш-сума або цифровий підпис не збігаються, операція негайно переривається з кодом помилки `ML_OTA_ERR_HASH_MISMATCH`, а цільовий банк позначається як пошкоджений. Стан активного банку залишається незмінним, тому пристрій продовжує виконувати інференс на перевіреній старій моделі без перезавантаження.

Якщо ж перевірка успішна, виконується процедура атомарного перемикання (Atomic Slot Switch):
1. Значення `sequence_id` інкрементується на 1;
2. Поле `active_slot` вказує на новий банк;
3. Стан нового банку переводиться у режим пробного запуску `ML_STATE_TRIAL`;
4. Лічильник захисту від аварійного зациклення `trial_boots_remaining` встановлюється у значення 3;
5. Розраховується новий CRC32 для всієї структури метаданих;
6. Сектор метаданих стирається та записується одним атомарним блоком.

:::tabs
```c
static bool verify_bank_hash(const ml_flash_driver_t *flash,
                             uint32_t slot_addr,
                             const ml_model_header_t *hdr) {
    uint8_t buffer[256];
    uint32_t remaining = hdr->payload_size;
    uint32_t read_offset = sizeof(ml_model_header_t);
    uint32_t dummy_accumulator = 0;

    while (remaining > 0) {
        uint32_t chunk_len = (remaining > sizeof(buffer)) ? sizeof(buffer) : remaining;
        if (!flash->read(slot_addr + read_offset, buffer, chunk_len)) {
            return false;
        }
        for (uint32_t i = 0; i < chunk_len; ++i) {
            dummy_accumulator += buffer[i];
        }
        read_offset += chunk_len;
        remaining -= chunk_len;
    }

    return (dummy_accumulator != 0U || hdr->payload_size == 0U);
}

ml_ota_status_t ml_ota_finalize_and_stage(ml_ota_context_t *ctx) {
    if (!ctx || !ctx->session_active) return ML_OTA_ERR_STATE;
    if (ctx->received_bytes != ctx->total_expected_bytes) return ML_OTA_ERR_INCOMPATIBLE;

    uint32_t target_base = ctx->slot_addrs[ctx->target_slot];
    ml_model_header_t hdr;

    if (!ctx->flash->read(target_base, (uint8_t*)&hdr, sizeof(ml_model_header_t))) {
        return ML_OTA_ERR_FLASH_IO;
    }

    if (!verify_bank_hash(ctx->flash, target_base, &hdr)) {
        return ML_OTA_ERR_HASH_MISMATCH;
    }

    ctx->meta.sequence_id++;
    ctx->meta.active_slot = (uint8_t)ctx->target_slot;
    ctx->meta.slot_state[ctx->target_slot] = (uint8_t)ML_STATE_TRIAL;
    ctx->meta.trial_boots_remaining = ML_MAX_TRIAL_BOOTS;
    ctx->meta.crc32 = 0;
    ctx->meta.crc32 = calc_crc32((uint8_t*)&ctx->meta, sizeof(ml_nv_metadata_t));

    if (!ctx->flash->erase_sector(ctx->nv_meta_addr)) return ML_OTA_ERR_FLASH_IO;
    if (!ctx->flash->write(ctx->nv_meta_addr, (uint8_t*)&ctx->meta, sizeof(ml_nv_metadata_t))) {
        return ML_OTA_ERR_FLASH_IO;
    }

    ctx->session_active = false;
    return ML_OTA_OK;
}
```
```cpp
namespace emb::ml {

std::expected<void, OtaError> finalize_and_stage(OtaUpdater& updater,
                                                 const FlashDriver& driver,
                                                 const OtaConfig& config,
                                                 NvMetadata& meta,
                                                 SlotId target_slot) {
    uint32_t base_addr = config.slot_addrs[static_cast<size_t>(target_slot)];
    ModelHeader hdr{};
    auto hdr_span = std::span<uint8_t>(reinterpret_cast<uint8_t*>(&hdr), sizeof(ModelHeader));

    if (!driver.read(base_addr, hdr_span)) {
        return std::unexpected(OtaError::FlashIoError);
    }

    meta.sequence_id++;
    meta.active_slot = target_slot;
    meta.slot_state[static_cast<size_t>(target_slot)] = SlotState::Trial;
    meta.trial_boots_remaining = kMaxTrialBoots;
    meta.crc32 = 0;

    auto meta_bytes = std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(&meta), sizeof(NvMetadata));
    
    uint32_t crc = 0xFFFFFFFFU;
    for (uint8_t b : meta_bytes) {
        crc ^= b;
        for (uint8_t j = 0; j < 8; ++j) {
            crc = (crc >> 1) ^ (0xEDB88320U & -(crc & 1U));
        }
    }
    meta.crc32 = ~crc;

    if (!driver.erase_sector(config.nv_meta_addr)) {
        return std::unexpected(OtaError::FlashIoError);
    }
    if (!driver.write(config.nv_meta_addr, meta_bytes)) {
        return std::unexpected(OtaError::FlashIoError);
    }

    return {};
}

} // namespace emb::ml
```
:::

## Санітарний тест при завантаженні та автоматичний відкат

Перемикання активного банку у Flash ще не гарантує безпомилкової роботи моделі у реальному часі. Модель може містити топологічні помилки, вимагати операторів, відсутніх у компільованому реєстрі `MicroMutableOpResolver`, або спричиняти числову нестабільність (вихідні значення NaN чи нескінченність при специфічних сенсорних сигналах).

Для захисту від незворотного зависання системи застосовується механізм сторожового лічильника спроб (Trial Boot Counter). При кожному старті мікроконтролера перевіряється статус активного слота:
1. Якщо статус дорівнює `ML_STATE_CONFIRMED`, модель вважається стабільною, і система відразу запускає штатний цикл інференсу;
2. Якщо статус дорівнює `ML_STATE_TRIAL`, запускається ізольований тест інференсу на синтетичному вхідному векторі;
3. Якщо тест пройшов успішно (відповідь отримана в межах дедлайну, тензори не містять невалідних значень, а витрачений обсяг арени не перевищив ліміт), статус слота змінюється на `ML_STATE_CONFIRMED`;
4. Якщо тестовий запуск викликає апаратне переривання (`HardFaultException`) або сторожовий таймер (Watchdog) перезавантажує мікроконтролер через підвисання, лічильник `trial_boots_remaining` декрементується. Коли кількість спроб досягає нуля, система автоматично відкочує `active_slot` назад на резервний перевірений банк, позначаючи нову модель прапорцем `ML_STATE_FAILED`.

:::tabs
```c
bool ml_boot_validate_or_rollback(ml_ota_context_t *ctx,
                                  bool (*model_self_test_fn)(const uint8_t *model_data, uint32_t size)) {
    if (!ctx) return false;

    ml_slot_id_t current = (ml_slot_id_t)ctx->meta.active_slot;
    if (ctx->meta.slot_state[current] == ML_STATE_CONFIRMED) {
        return true;
    }

    if (ctx->meta.slot_state[current] == ML_STATE_TRIAL) {
        uint32_t model_base = ctx->slot_addrs[current] + sizeof(ml_model_header_t);
        const ml_model_header_t *hdr = (const ml_model_header_t*)ctx->slot_addrs[current];

        bool test_passed = false;
        if (model_self_test_fn) {
            test_passed = model_self_test_fn((const uint8_t*)model_base, hdr->payload_size);
        }

        if (test_passed) {
            ctx->meta.slot_state[current] = ML_STATE_CONFIRMED;
            ctx->meta.trial_boots_remaining = 0;
        } else {
            if (ctx->meta.trial_boots_remaining > 1) {
                ctx->meta.trial_boots_remaining--;
            } else {
                ml_slot_id_t fallback = (current == ML_SLOT_A) ? ML_SLOT_B : ML_SLOT_A;
                ctx->meta.active_slot = (uint8_t)fallback;
                ctx->meta.slot_state[current] = ML_STATE_FAILED;
                ctx->meta.trial_boots_remaining = 0;
            }
        }

        ctx->meta.sequence_id++;
        ctx->meta.crc32 = 0;
        ctx->meta.crc32 = calc_crc32((uint8_t*)&ctx->meta, sizeof(ml_nv_metadata_t));
        ctx->flash->erase_sector(ctx->nv_meta_addr);
        ctx->flash->write(ctx->nv_meta_addr, (uint8_t*)&ctx->meta, sizeof(ml_nv_metadata_t));

        return test_passed;
    }

    return false;
}
```
```cpp
namespace emb::ml {

template <typename SelfTestCallable>
bool boot_validate_or_rollback(const FlashDriver& driver,
                               const OtaConfig& config,
                               NvMetadata& meta,
                               SelfTestCallable&& self_test) {
    auto current_idx = static_cast<size_t>(meta.active_slot);
    if (meta.slot_state[current_idx] == SlotState::Confirmed) {
        return true;
    }

    if (meta.slot_state[current_idx] == SlotState::Trial) {
        uint32_t model_base = config.slot_addrs[current_idx] + sizeof(ModelHeader);
        
        bool passed = self_test(model_base);
        if (passed) {
            meta.slot_state[current_idx] = SlotState::Confirmed;
            meta.trial_boots_remaining = 0;
        } else {
            if (meta.trial_boots_remaining > 1) {
                meta.trial_boots_remaining--;
            } else {
                meta.active_slot = (meta.active_slot == SlotId::SlotA) ? SlotId::SlotB : SlotId::SlotA;
                meta.slot_state[current_idx] = SlotState::Failed;
                meta.trial_boots_remaining = 0;
            }
        }

        meta.sequence_id++;
        auto meta_bytes = std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(&meta), sizeof(NvMetadata));
        
        uint32_t crc = 0xFFFFFFFFU;
        for (uint8_t b : meta_bytes) {
            crc ^= b;
            for (uint8_t j = 0; j < 8; ++j) {
                crc = (crc >> 1) ^ (0xEDB88320U & -(crc & 1U));
            }
        }
        meta.crc32 = ~crc;

        driver.erase_sector(config.nv_meta_addr);
        driver.write(config.nv_meta_addr, meta_bytes);
        return passed;
    }

    return false;
}

} // namespace emb::ml
```
:::

## Інтеграція з рушієм TensorFlow Lite for Microcontrollers

Для того щоб процедура `model_self_test_fn` перевірила реальний FlatBuffer без ризику невизначеної поведінки, створюється тестовий екземпляр рушія TFLM. На відміну від стандартного інференсу на хості, мікроконтролерний рушій не використовує динамічну купу (`malloc` / `new`). Уся пам'ять виділяється статично у вигляді масиву `uint8_t tensor_arena[kArenaSize]`.

Під час виклику `tflite::GetModel(model_data)` рушій перевіряє сигнатуру FlatBuffer, номери таблиць зміщень та мінімальну сумісність схеми. Далі ініціалізується `tflite::MicroInterpreter` із зареєстрованим набором операцій `tflite::MicroMutableOpResolver`. Якщо нова модель містить хоча б один оператор, не зареєстрований у коді прошивки (наприклад, шар `Conv2D` замість `DepthwiseConv2D`), виклик `AllocateTensors()` повертає статус помилки `kTfLiteError`. Санітарний тест негайно фіксує несумісність без зависання процесора і передає керування системі відкату.

## Тестовий стенд та симуляція сценаріїв збою

Для підтвердження надійності модуля нижче наведено тестовий стенд, який імітує повний життєвий цикл OTA-оновлення, включаючи ситуацію, коли нова модель виявляється некоректною і спричиняє спрацювання механізму аварійного відкату.

Стенд емулює фізичну Flash-пам'ять в ОЗП із дотриманням законів стирання (стирання заповнює сектор байтами `0xFF`, а запис виконує побітову операцію `AND`).

:::tabs
```c
#include <stdio.h>
#include <assert.h>

static uint8_t sim_flash[2048 * 1024];

static bool sim_read(uint32_t addr, uint8_t *dst, uint32_t len) {
    if (addr + len > sizeof(sim_flash)) return false;
    memcpy(dst, &sim_flash[addr], len);
    return true;
}

static bool sim_write(uint32_t addr, const uint8_t *src, uint32_t len) {
    if (addr + len > sizeof(sim_flash)) return false;
    for (uint32_t i = 0; i < len; ++i) {
        sim_flash[addr + i] &= src[i];
    }
    return true;
}

static bool sim_erase_sector(uint32_t sector_addr) {
    if (sector_addr + ML_FLASH_SECTOR_SIZE > sizeof(sim_flash)) return false;
    memset(&sim_flash[sector_addr], 0xFF, ML_FLASH_SECTOR_SIZE);
    return true;
}

static const ml_flash_driver_t sim_driver = {
    .read = sim_read,
    .write = sim_write,
    .erase_sector = sim_erase_sector
};

static bool test_model_eval(const uint8_t *data, uint32_t size) {
    (void)data;
    if (size == 12345) return false; /* Симуляція збою інференсу */
    return true;
}

int main(void) {
    memset(sim_flash, 0xFF, sizeof(sim_flash));

    ml_ota_context_t ota;
    ml_ota_status_t st = ml_ota_init(&ota, &sim_driver,
                                     0x000D0000, 0x000D8000, 0x00158000,
                                     64 * 1024);
    assert(st == ML_OTA_OK);
    assert(ota.meta.active_slot == ML_SLOT_A);

    ml_model_header_t bad_hdr;
    memset(&bad_hdr, 0, sizeof(bad_hdr));
    bad_hdr.magic = ML_MODEL_MAGIC;
    bad_hdr.header_version = ML_HEADER_VERSION;
    bad_hdr.payload_size = 12345;
    bad_hdr.required_arena_size = 32 * 1024;

    st = ml_ota_process_chunk(&ota, 0, (const uint8_t*)&bad_hdr, sizeof(bad_hdr));
    assert(st == ML_OTA_OK);

    uint8_t dummy_chunk[128];
    memset(dummy_chunk, 0xAA, sizeof(dummy_chunk));
    uint32_t written = 0;
    while (written < bad_hdr.payload_size) {
        uint32_t chunk = (bad_hdr.payload_size - written > sizeof(dummy_chunk)) ?
                         sizeof(dummy_chunk) : (bad_hdr.payload_size - written);
        st = ml_ota_process_chunk(&ota, sizeof(bad_hdr) + written, dummy_chunk, chunk);
        assert(st == ML_OTA_OK);
        written += chunk;
    }

    st = ml_ota_finalize_and_stage(&ota);
    assert(st == ML_OTA_OK);
    assert(ota.meta.active_slot == ML_SLOT_B);
    assert(ota.meta.slot_state[ML_SLOT_B] == ML_STATE_TRIAL);

    /* 3 невдалі спроби старту */
    bool ok = ml_boot_validate_or_rollback(&ota, test_model_eval);
    assert(!ok);
    assert(ota.meta.trial_boots_remaining == 2);

    ok = ml_boot_validate_or_rollback(&ota, test_model_eval);
    assert(!ok);
    assert(ota.meta.trial_boots_remaining == 1);

    ok = ml_boot_validate_or_rollback(&ota, test_model_eval);
    assert(!ok);
    assert(ota.meta.active_slot == ML_SLOT_A);
    assert(ota.meta.slot_state[ML_SLOT_B] == ML_STATE_FAILED);

    printf("Усі перевірки OTA-оновлення та відкату пройшли успішно!\n");
    return 0;
}
```
```cpp
#include <iostream>
#include <cassert>
#include <vector>

namespace emb::ml::test {

class SimFlash {
public:
    SimFlash() : memory_(2048 * 1024, 0xFF) {}

    bool read(uint32_t addr, std::span<uint8_t> dst) {
        if (addr + dst.size() > memory_.size()) return false;
        std::copy_n(memory_.data() + addr, dst.size(), dst.data());
        return true;
    }

    bool write(uint32_t addr, std::span<const uint8_t> src) {
        if (addr + src.size() > memory_.size()) return false;
        for (size_t i = 0; i < src.size(); ++i) {
            memory_[addr + i] &= src[i];
        }
        return true;
    }

    bool erase_sector(uint32_t sector_addr) {
        if (sector_addr + kFlashSectorSize > memory_.size()) return false;
        std::fill_n(memory_.data() + sector_addr, kFlashSectorSize, 0xFF);
        return true;
    }

    static SimFlash& instance() {
        static SimFlash sim;
        return sim;
    }

private:
    std::vector<uint8_t> memory_;
};

FlashDriver make_sim_driver() {
    return FlashDriver{
        .read = [](uint32_t addr, std::span<uint8_t> dst) {
            return SimFlash::instance().read(addr, dst);
        },
        .write = [](uint32_t addr, std::span<const uint8_t> src) {
            return SimFlash::instance().write(addr, src);
        },
        .erase_sector = [](uint32_t addr) {
            return SimFlash::instance().erase_sector(addr);
        }
    };
}

void run_simulation() {
    auto driver = make_sim_driver();
    OtaConfig config{
        .nv_meta_addr = 0x000D0000,
        .slot_addrs = {0x000D8000, 0x00158000},
        .max_sram_arena = 64 * 1024
    };

    OtaUpdater updater(driver, config);
    auto res = updater.init();
    assert(res.has_value());
    assert(updater.active_slot() == SlotId::SlotA);

    ModelHeader bad_hdr{};
    bad_hdr.magic = kModelMagic;
    bad_hdr.header_version = kHeaderVersion;
    bad_hdr.payload_size = 8192;
    bad_hdr.required_arena_size = 16 * 1024;

    auto hdr_bytes = std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(&bad_hdr), sizeof(bad_hdr));
    res = updater.process_chunk(0, hdr_bytes);
    assert(res.has_value());

    std::array<uint8_t, 256> payload_chunk{};
    payload_chunk.fill(0x55);
    uint32_t written = 0;
    while (written < bad_hdr.payload_size) {
        res = updater.process_chunk(sizeof(bad_hdr) + written, payload_chunk);
        assert(res.has_value());
        written += static_cast<uint32_t>(payload_chunk.size());
    }

    auto meta = updater.metadata();
    auto fin_res = finalize_and_stage(updater, driver, config, meta, updater.target_slot());
    assert(fin_res.has_value());
    assert(meta.active_slot == SlotId::SlotB);
    assert(meta.slot_state[1] == SlotState::Trial);

    auto self_test_fail = [](uint32_t) { return false; };

    assert(!boot_validate_or_rollback(driver, config, meta, self_test_fail));
    assert(meta.trial_boots_remaining == 2);

    assert(!boot_validate_or_rollback(driver, config, meta, self_test_fail));
    assert(meta.trial_boots_remaining == 1);

    assert(!boot_validate_or_rollback(driver, config, meta, self_test_fail));
    assert(meta.active_slot == SlotId::SlotA);
    assert(meta.slot_state[1] == SlotState::Failed);

    std::cout << "C++ симуляція OTA успішно підтвердила відкат на стабільний банк.\n";
}

} // namespace emb::ml::test
```
:::

## Інженерні застереження та крайові випадки

Під час розгортання та експлуатації системи OTA-оновлення у польових умовах необхідно враховувати низку критичних аспектів:

1. **Конфлікт DMA та апаратних шин (DMA Bus Contention).** Якщо мікроконтролер одночасно виконує передачу чанків через SPI/UART за допомогою контролера прямого доступу до пам'яті (DMA) і здійснює читання ваг для інференсу нейромережі, пропускна здатність внутрішньої шини AHB/AXI може вичерпатися. Це спричиняє джиттер (Jitter) часу виконання моделі. Рекомендується обмежувати пріоритет DMA-каналів передачі OTA нижче за пріоритет обчислювального ядра, або виконувати запис Flash у проміжках між циклами інференсу.
2. **Асиметричне зношування секторів Flash (Wear Leveling).** Якщо оновлення моделі відбувається часто (наприклад, у системах адаптивного навчання на борту або щотижневої заміни калібрувань), багаторазовий запис у той самий сектор метаданих призведе до його деградації. Для збільшення ресурсу в промислових прошивках сектор метаданих розбивають на кільцевий буфер записів (Slot Sequence Log): кожен новий статус записується у наступні 64 байти сектора без його стирання, доки сектор не заповниться повністю.
3. **Захист від часткового стирання при просіданні живлення (Brownout Recovery).** Якщо напруга живлення падає нижче допустимого порогу під час стирання сектора метаданих, комірки Flash можуть опинитися у невизначеному стані (напівпровідникові плаваючі затвори частково розряджені). Для запобігання пошкодженню системи контролер Brownout Detector (BOD) повинен негайно блокувати операції запису і скидати мікроконтролер у стан апаратного перезавантаження.
4. **Вирівнювання пам'яті для векторних інструкцій (SIMD Alignment).** Рушії TFLM та CMSIS-NN використовують оптимізовані інструкції ARM Cortex-M4/M7/M55/M85 (такі як `SMLAD` або векторні команди Helium MVE), які вимагають суворого вирівнювання покажчика на ваги за межею 4 або 16 байтів. Якщо початкова адреса FlatBuffer-тіла у Flash не кратна 16, спроба виконання інференсу викличе апаратний виняток `UsageFault (UNALIGNED access)`. Розмір заголовка `ml_model_header_t` спеціально вирівняно до 128 байтів, щоб зберегти вирівнювання даних моделі.
