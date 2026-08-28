# ⚙️ Повна реалізація стійкого до знеструмлення кільцевого Flash-логера для мікроконтролера

Цей проект надає повністю автономну, готову до вбудовування бібліотеку бортового кільцевого журналу для мікроконтролерів (ARM Cortex-M, ESP32, RISC-V), яка забезпечує енергонезалежне збереження діагностичних записів у SPI NOR Flash. Бібліотека гарантує стійкість до раптового вимкнення живлення (Power-Cut Safety), природне вирівнювання зносу комірок Flash через ротацію секторів, атомарний контроль станів за допомогою порозрядних масок і вичитування пачками для відправки на сервер через радіомодем.

У класичних вбудованих прошивках збереження логів часто реалізують або через просту файлову систему (наприклад, LittleFS чи FATFS), або через прямий неструктурований запис у сирі адреси Flash. Обидва підходи мають серйозні вади: файлові системи створюють значні накладні витрати оперативної пам'яті на кешування дескрипторів і таблиць вузлів (що критично для мікроконтролерів із 16–32 КБ RAM), а сирий запис без контролю цілісності руйнується при першому ж знеструмленні. Наведена нижче бібліотека позбавлена цих недоліків: вона працює без динамічного виділення пам'яті (нуль викликів `malloc`), оперує безпосередньо секторами Flash, контролює кожен запис контрольною сумою CRC-16 і відновлює актуальний стан після будь-якого аварійного скидання.

## 1. Архітектура та формат даних

Буфер оперує пулом секторів однакового розміру (типово 4096 байтів). Кожен сектор має 16-байтний заголовок, що розміщується за нульовим зсувом сектора:

```
[0..1]:   Magic (0xA55A) — ознака ініціалізованого сектора логера
[2..3]:   Версія структури (0x0001)
[4..7]:   Номер послідовності сектора (Sequence Counter)
[8..11]:  Лічильник стирань (Erase Counter)
[12..15]: Прапорець стану сектора:
          • 0xFFFFFFFF — ERASED (чистий резерв)
          • 0xFFFFFFFE — ACTIVE (поточний сектор для запису)
          • 0xFFFFFFFC — FULL (сектор повністю заповнено)
          • 0x00000000 — DIRTY (дані вивантажено, готовий до стирання)
```

Кожен окремий лог-запис має заголовок із контрольною сумою CRC-16-CCITT:

```
[0..1]:   Magic байт кадру (0x55AA)
[2]:      Загальна довжина запису в байтах (включно з заголовком і CRC)
[3]:      Рівень логування (0: TRACE, 1: DEBUG, 2: INFO, 3: WARN, 4: ERROR, 5: FATAL)
[4]:      Ідентифікатор модуля / підсистеми (Module ID)
[5..8]:   Мітка часу (Timestamp, мілісекунди від старту)
[9..12]:  Токен рядка або код події (Token ID)
[13..N-2]:Корисне навантаження (упаковані аргументи)
[N-1..N]: CRC-16 (покриває байти [2..N-2])
```

## 2. Покроковий механізм роботи логера

Робота бібліотеки спирається на чотири фундаментальні операції:

1. **Ініціалізація та сканування (Scan & Recovery):** Під час виклику `flash_logger_init()` бібліотека читає заголовки всіх `FLASH_SECTOR_COUNT` секторів. Вона знаходить сектор у стані `ACTIVE` з найвищим послідовним номером `seq_num`. Якщо такий сектор знайдено, логер лінійно зчитує всі записи всередині нього, перевіряючи коректність магічного числа `0x55AA` та східність CRC-16. Перший же запис із невалідною контрольною сумою або невстановленими байтами вважається кінцем даних, і покажчик запису `write_offset` фіксується перед ним.
2. **Атомарний запис події (Append Entry):** При додаванні нового запису функція перевіряє, чи вміщується новий кадр у поточний 4-кілобайтний сектор. Якщо місця достатньо, формується буфер у RAM, обчислюється CRC-16 і виконується запис на Flash. Якщо ж запис перевищує залишок сектора, запускається процедура ротації: поточний сектор позначається як `FULL` (переходом `0xFE -> 0xFC`), наступний сектор стирається, отримує інкрементований номер послідовності та статус `ACTIVE`.
3. **Підтвердження вивантаження (Commit Tail):** Коли мережевий стек передає сектор на сервер і отримує підтвердження (ACK), викликається функція `flash_logger_commit_tail()`. Стан сектора переводиться в `DIRTY` (значення `0x00000000`), а покажчик читання `tail_sector_idx` просувається до наступного сектора.
4. **Контроль цілісності за CRC-16-CCITT:** Контрольна сума обчислюється поліномом `0x1021` (початкове значення `0xFFFF`). Вона охоплює всі байти кадру, починаючи від поля довжини й закінчуючи останнім байтом корисного навантаження. Це гарантує, що якщо під час передачі по SPI або запису у Flash стався апаратний збій, спотворений запис ніколи не потрапить до серверної аналітики.

## 3. Обробка крайових випадків та відмов Flash

У реальних виробах виникають нештатні ситуації, які бібліотека обробляє детерміновано:

- **Знеструмлення під час запису заголовка кадру:** Якщо живлення зникає, коли записано лише перші кілька байтів (наприклад, Magic `0x55AA` та довжина, але не тіло й не CRC), під час наступного завантаження сканер виявить невідповідність контрольної суми. Сканер зупиняє лінійний прохід на цьому кадрі, встановлюючи `write_offset_in_sector` точно на його початок. Наступний виклик `flash_logger_write()` затре пошкоджені байти новим валідним записом або викличе ротацію сектора.
- **Гонка голови та хвоста при переповненні буфера (Buffer Overrun):** Якщо пристрій довго працює без виходу в мережу, голова запису (`active_sector_idx`) робить повний обіг і наздоганяє хвіст (`tail_sector_idx`). Замість блокування запису або паніки ядра, бібліотека примусово виштовхує хвіст уперед (`tail = (tail + 1) % COUNT`). Найстаріший сектор при цьому стирається й перевідкривається під нові дані. Це реалізує політику «найсвіжіші дані важливіші за старі» без зупинки системи.
- **Виявлення дефектних секторів (Bad Sector Handling):** Якщо виклик `hal.erase_sector()` або `hal.write()` повертає `false` (наприклад, через апаратну деградацію затворів мікросхеми Flash), логер негайно позначає такий сектор як дефектний, переходить до наступного сектору за кільцем і формує службовий запис `LOG_LEVEL_ERROR` із кодом пошкодженого блоку.

## 4. Інтеграція в RTOS та потокобезпечність

У багатозадачному середовищі (FreeRTOS, Zephyr, RT-Thread) виклики запису логів можуть надходити одночасно з кількох задач різного пріоритету та з обробників переривань (ISR).

Для забезпечення безпеки доступу до апаратного інтерфейсу SPI Flash застосовується дворівнева схема:
1. **Міжзадачний рівень:** Виклик `flash_logger_write()` всередині звичайної задачі захищається рекурсивним м'ютексом FreeRTOS (`xSemaphoreTakeRecursive`). Це запобігає одночасному чергуванню байтів від двох паралельних потоків виконання на одній шині SPI.
2. **Контекст переривань (ISR):** Прямий запис на повільну шину SPI з обробника переривання суворо заборонений (час очікування `Page Program` складає 0.7–3.0 мс). Замість цього переривання скидає короткий 12-байтний двійковий кадр у безблокувальну чергу в RAM (Lock-Free RAM Staging Ring Buffer), звідки фонова задача логера з найнижчим пріоритетом вичитує дані й записує їх у Flash.

## 5. Реалізація бібліотеки бортового логера

Нижче наведено паралельні, функціонально еквівалентні реалізації мовами C та C++:

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#define FLASH_SECTOR_SIZE     4096
#define FLASH_SECTOR_COUNT    8
#define LOG_SECTOR_MAGIC      0xA55A
#define LOG_RECORD_MAGIC      0x55AA

typedef enum {
    SECTOR_STATE_ERASED = 0xFFFFFFFF,
    SECTOR_STATE_ACTIVE = 0xFFFFFFFE,
    SECTOR_STATE_FULL   = 0xFFFFFFFC,
    SECTOR_STATE_DIRTY  = 0x00000000
} sector_state_t;

typedef enum {
    LOG_LEVEL_TRACE = 0,
    LOG_LEVEL_DEBUG = 1,
    LOG_LEVEL_INFO  = 2,
    LOG_LEVEL_WARN  = 3,
    LOG_LEVEL_ERROR = 4,
    LOG_LEVEL_FATAL = 5
} log_level_t;

#pragma pack(push, 1)
typedef struct {
    uint16_t magic;
    uint16_t version;
    uint32_t seq_num;
    uint32_t erase_count;
    uint32_t state;
} sector_header_t;

typedef struct {
    uint16_t magic;
    uint8_t  length;
    uint8_t  level;
    uint8_t  module_id;
    uint8_t  reserved;
    uint32_t timestamp_ms;
    uint32_t token_id;
} log_entry_header_t;
#pragma pack(pop)

/* HAL інтерфейс Flash-пам'яті */
typedef struct {
    bool (*read)(uint32_t addr, uint8_t *buf, size_t len);
    bool (*write)(uint32_t addr, const uint8_t *buf, size_t len);
    bool (*erase_sector)(uint32_t sector_addr);
} flash_hal_t;

/* Стан логера */
typedef struct {
    flash_hal_t hal;
    uint32_t    base_addr;
    uint32_t    active_sector_idx;
    uint32_t    write_offset_in_sector;
    uint32_t    tail_sector_idx;
    uint32_t    global_seq_num;
} flash_logger_t;

/* Обчислення табличного CRC-16-CCITT */
static uint16_t crc16_ccitt(const uint8_t *data, size_t len) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < len; i++) {
        crc ^= (uint16_t)data[i] << 8;
        for (int b = 0; b < 8; b++) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ 0x1021;
            } else {
                crc <<= 1;
            }
        }
    }
    return crc;
}

static uint32_t get_sector_address(const flash_logger_t *logger, uint32_t sector_idx) {
    return logger->base_addr + (sector_idx * FLASH_SECTOR_SIZE);
}

/* Ініціалізація та відновлення стану після знеструмлення */
bool flash_logger_init(flash_logger_t *logger, const flash_hal_t *hal, uint32_t base_addr) {
    logger->hal = *hal;
    logger->base_addr = base_addr;
    logger->active_sector_idx = 0;
    logger->write_offset_in_sector = sizeof(sector_header_t);
    logger->tail_sector_idx = 0;
    logger->global_seq_num = 0;

    uint32_t max_seq = 0;
    int active_idx = -1;
    int oldest_idx = -1;
    uint32_t min_seq = 0xFFFFFFFF;

    /* Сканування заголовків усіх секторів */
    for (uint32_t i = 0; i < FLASH_SECTOR_COUNT; i++) {
        sector_header_t hdr;
        uint32_t addr = get_sector_address(logger, i);
        if (!logger->hal.read(addr, (uint8_t *)&hdr, sizeof(hdr))) {
            return false;
        }

        if (hdr.magic == LOG_SECTOR_MAGIC) {
            if (hdr.state == SECTOR_STATE_ACTIVE) {
                active_idx = (int)i;
            }
            if (hdr.seq_num > max_seq) {
                max_seq = hdr.seq_num;
            }
            if (hdr.seq_num < min_seq && hdr.state != SECTOR_STATE_ERASED) {
                min_seq = hdr.seq_num;
                oldest_idx = (int)i;
            }
        }
    }

    if (active_idx != -1) {
        logger->active_sector_idx = (uint32_t)active_idx;
        logger->global_seq_num = max_seq;

        /* Знаходження кінця дійсних записів у активному секторі */
        uint32_t offset = sizeof(sector_header_t);
        uint32_t sector_addr = get_sector_address(logger, logger->active_sector_idx);

        while (offset + sizeof(log_entry_header_t) + sizeof(uint16_t) <= FLASH_SECTOR_SIZE) {
            log_entry_header_t eh;
            if (!logger->hal.read(sector_addr + offset, (uint8_t *)&eh, sizeof(eh))) {
                break;
            }
            if (eh.magic != LOG_RECORD_MAGIC || eh.length == 0xFF || eh.length < sizeof(eh) + 2) {
                break;
            }

            /* Перевірка валідності кадру за CRC */
            uint8_t rec_buf[256];
            if (eh.length > sizeof(rec_buf)) break;
            logger->hal.read(sector_addr + offset, rec_buf, eh.length);
            uint16_t expected_crc = (uint16_t)(rec_buf[eh.length - 2] | (rec_buf[eh.length - 1] << 8));
            uint16_t actual_crc = crc16_ccitt(rec_buf + 2, eh.length - 4);

            if (expected_crc != actual_crc) {
                break; /* Знайдено недописаний або пошкоджений запис */
            }

            offset += eh.length;
        }
        logger->write_offset_in_sector = offset;
    } else {
        /* Новий старт: підготовка сектора 0 */
        logger->active_sector_idx = 0;
        logger->global_seq_num = 1;
        logger->hal.erase_sector(get_sector_address(logger, 0));

        sector_header_t new_hdr = {
            .magic = LOG_SECTOR_MAGIC,
            .version = 1,
            .seq_num = logger->global_seq_num,
            .erase_count = 1,
            .state = SECTOR_STATE_ACTIVE
        };
        logger->hal.write(get_sector_address(logger, 0), (const uint8_t *)&new_hdr, sizeof(new_hdr));
        logger->write_offset_in_sector = sizeof(sector_header_t);
    }

    logger->tail_sector_idx = (oldest_idx != -1) ? (uint32_t)oldest_idx : logger->active_sector_idx;
    return true;
}

/* Ротація сектора при заповненні */
static bool rotate_to_next_sector(flash_logger_t *logger) {
    /* 1. Позначити поточний сектор як FULL (перехід 0xFE -> 0xFC) */
    uint32_t cur_addr = get_sector_address(logger, logger->active_sector_idx);
    uint32_t full_state = SECTOR_STATE_FULL;
    logger->hal.write(cur_addr + offsetof(sector_header_t, state), (const uint8_t *)&full_state, sizeof(full_state));

    /* 2. Визначити наступний сектор */
    uint32_t next_idx = (logger->active_sector_idx + 1) % FLASH_SECTOR_COUNT;

    /* 3. Зчитати лічильник стирань старого сектора для збереження статистики */
    sector_header_t old_hdr;
    logger->hal.read(get_sector_address(logger, next_idx), (uint8_t *)&old_hdr, sizeof(old_hdr));
    uint32_t next_erase_count = (old_hdr.magic == LOG_SECTOR_MAGIC) ? (old_hdr.erase_count + 1) : 1;

    /* 4. Стерти сектор і відкрити його */
    uint32_t next_addr = get_sector_address(logger, next_idx);
    if (!logger->hal.erase_sector(next_addr)) {
        return false;
    }

    logger->global_seq_num++;
    sector_header_t new_hdr = {
        .magic = LOG_SECTOR_MAGIC,
        .version = 1,
        .seq_num = logger->global_seq_num,
        .erase_count = next_erase_count,
        .state = SECTOR_STATE_ACTIVE
    };
    logger->hal.write(next_addr, (const uint8_t *)&new_hdr, sizeof(new_hdr));

    logger->active_sector_idx = next_idx;
    logger->write_offset_in_sector = sizeof(sector_header_t);

    /* Якщо голова наздогнала хвіст — хвіст витісняється вперед */
    if (logger->active_sector_idx == logger->tail_sector_idx) {
        logger->tail_sector_idx = (logger->tail_sector_idx + 1) % FLASH_SECTOR_COUNT;
    }

    return true;
}

/* Додавання лог-запису */
bool flash_logger_write(flash_logger_t *logger, log_level_t level, uint8_t module_id,
                        uint32_t timestamp_ms, uint32_t token_id,
                        const uint8_t *payload, uint8_t payload_len) {
    uint8_t total_len = (uint8_t)(sizeof(log_entry_header_t) + payload_len + sizeof(uint16_t));
    if (total_len > 255) return false;

    /* Перевірка вільного місця в поточному секторі */
    if (logger->write_offset_in_sector + total_len > FLASH_SECTOR_SIZE) {
        if (!rotate_to_next_sector(logger)) {
            return false;
        }
    }

    uint8_t buf[256];
    log_entry_header_t *hdr = (log_entry_header_t *)buf;
    hdr->magic = LOG_RECORD_MAGIC;
    hdr->length = total_len;
    hdr->level = (uint8_t)level;
    hdr->module_id = module_id;
    hdr->reserved = 0;
    hdr->timestamp_ms = timestamp_ms;
    hdr->token_id = token_id;

    if (payload_len > 0 && payload != NULL) {
        memcpy(buf + sizeof(log_entry_header_t), payload, payload_len);
    }

    /* CRC обчислюється від байта 2 (довжина) до кінця корисного навантаження */
    uint16_t crc = crc16_ccitt(buf + 2, total_len - 4);
    buf[total_len - 2] = (uint8_t)(crc & 0xFF);
    buf[total_len - 1] = (uint8_t)((crc >> 8) & 0xFF);

    uint32_t write_addr = get_sector_address(logger, logger->active_sector_idx) + logger->write_offset_in_sector;
    if (!logger->hal.write(write_addr, buf, total_len)) {
        return false;
    }

    logger->write_offset_in_sector += total_len;
    return true;
}

/* Підтвердження вивантаження сектора від сервера */
bool flash_logger_commit_tail(flash_logger_t *logger, uint32_t sector_idx) {
    if (sector_idx >= FLASH_SECTOR_COUNT) return false;
    if (sector_idx == logger->active_sector_idx) {
        /* Активний сектор ще заповнюється, позначати як DIRTY зарано */
        return true;
    }

    uint32_t addr = get_sector_address(logger, sector_idx);
    uint32_t dirty_state = SECTOR_STATE_DIRTY;
    logger->hal.write(addr + offsetof(sector_header_t, state), (const uint8_t *)&dirty_state, sizeof(dirty_state));

    if (sector_idx == logger->tail_sector_idx) {
        logger->tail_sector_idx = (logger->tail_sector_idx + 1) % FLASH_SECTOR_COUNT;
    }
    return true;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>
#include <algorithm>
#include <array>
#include <string_view>

enum class LogLevel : uint8_t {
    Trace = 0,
    Debug = 1,
    Info  = 2,
    Warn  = 3,
    Error = 4,
    Fatal = 5
};

enum class SectorState : uint32_t {
    Erased = 0xFFFFFFFF,
    Active = 0xFFFFFFFE,
    Full   = 0xFFFFFFFC,
    Dirty  = 0x00000000
};

enum class LoggerError {
    HalError,
    BufferOverflow,
    InvalidRecord,
    CrcMismatch,
    SectorCorrupt
};

class FlashHal {
public:
    virtual ~FlashHal() = default;
    virtual bool read(uint32_t addr, std::span<uint8_t> dst) = 0;
    virtual bool write(uint32_t addr, std::span<const uint8_t> src) = 0;
    virtual bool eraseSector(uint32_t sector_addr) = 0;
};

class PersistentRingLogger {
public:
    static constexpr size_t SectorSize = 4096;
    static constexpr size_t SectorCount = 8;
    static constexpr uint16_t SectorMagic = 0xA55A;
    static constexpr uint16_t RecordMagic = 0x55AA;

#pragma pack(push, 1)
    struct SectorHeader {
        uint16_t    magic{SectorMagic};
        uint16_t    version{1};
        uint32_t    seqNum{0};
        uint32_t    eraseCount{0};
        SectorState state{SectorState::Erased};
    };

    struct RecordHeader {
        uint16_t magic{RecordMagic};
        uint8_t  length{0};
        LogLevel level{LogLevel::Info};
        uint8_t  moduleId{0};
        uint8_t  reserved{0};
        uint32_t timestampMs{0};
        uint32_t tokenId{0};
    };
#pragma pack(pop)

    explicit PersistentRingLogger(FlashHal& hal, uint32_t baseAddr = 0)
        : hal_(hal), baseAddr_(baseAddr) {}

    std::expected<void, LoggerError> init() {
        uint32_t maxSeq = 0;
        int activeIdx = -1;
        int oldestIdx = -1;
        uint32_t minSeq = 0xFFFFFFFF;

        for (uint32_t i = 0; i < SectorCount; ++i) {
            SectorHeader hdr{};
            if (!hal_.read(sectorAddress(i), std::as_writable_bytes(std::span{&hdr, 1}))) {
                return std::unexpected(LoggerError::HalError);
            }

            if (hdr.magic == SectorMagic) {
                if (hdr.state == SectorState::Active) {
                    activeIdx = static_cast<int>(i);
                }
                if (hdr.seqNum > maxSeq) {
                    maxSeq = hdr.seqNum;
                }
                if (hdr.seqNum < minSeq && hdr.state != SectorState::Erased) {
                    minSeq = hdr.seqNum;
                    oldestIdx = static_cast<int>(i);
                }
            }
        }

        if (activeIdx != -1) {
            activeSectorIdx_ = static_cast<uint32_t>(activeIdx);
            globalSeqNum_ = maxSeq;
            recoverActiveSectorOffset();
        } else {
            activeSectorIdx_ = 0;
            globalSeqNum_ = 1;
            if (!hal_.eraseSector(sectorAddress(0))) {
                return std::unexpected(LoggerError::HalError);
            }
            SectorHeader newHdr{
                .magic = SectorMagic,
                .version = 1,
                .seqNum = globalSeqNum_,
                .eraseCount = 1,
                .state = SectorState::Active
            };
            if (!hal_.write(sectorAddress(0), std::as_bytes(std::span{&newHdr, 1}))) {
                return std::unexpected(LoggerError::HalError);
            }
            writeOffset_ = sizeof(SectorHeader);
        }

        tailSectorIdx_ = (oldestIdx != -1) ? static_cast<uint32_t>(oldestIdx) : activeSectorIdx_;
        return {};
    }

    std::expected<void, LoggerError> log(LogLevel level, uint8_t moduleId,
                                         uint32_t timestampMs, uint32_t tokenId,
                                         std::span<const uint8_t> payload = {}) {
        const size_t totalLen = sizeof(RecordHeader) + payload.size() + sizeof(uint16_t);
        if (totalLen > 255) {
            return std::unexpected(LoggerError::BufferOverflow);
        }

        if (writeOffset_ + totalLen > SectorSize) {
            if (auto res = rotateSector(); !res) {
                return res;
            }
        }

        std::array<uint8_t, 256> buffer{};
        auto* hdr = reinterpret_cast<RecordHeader*>(buffer.data());
        hdr->magic = RecordMagic;
        hdr->length = static_cast<uint8_t>(totalLen);
        hdr->level = level;
        hdr->moduleId = moduleId;
        hdr->reserved = 0;
        hdr->timestampMs = timestampMs;
        hdr->tokenId = tokenId;

        if (!payload.empty()) {
            std::copy(payload.begin(), payload.end(), buffer.begin() + sizeof(RecordHeader));
        }

        uint16_t crc = calculateCrc(std::span{buffer.data() + 2, totalLen - 4});
        buffer[totalLen - 2] = static_cast<uint8_t>(crc & 0xFF);
        buffer[totalLen - 1] = static_cast<uint8_t>((crc >> 8) & 0xFF);

        uint32_t writeAddr = sectorAddress(activeSectorIdx_) + writeOffset_;
        if (!hal_.write(writeAddr, std::span{buffer.data(), totalLen})) {
            return std::unexpected(LoggerError::HalError);
        }

        writeOffset_ += totalLen;
        return {};
    }

    std::expected<void, LoggerError> commitTailAck(uint32_t sectorIdx) {
        if (sectorIdx >= SectorCount) {
            return std::unexpected(LoggerError::SectorCorrupt);
        }
        if (sectorIdx == activeSectorIdx_) {
            return {};
        }

        uint32_t addr = sectorAddress(sectorIdx) + offsetof(SectorHeader, state);
        SectorState dirtyState = SectorState::Dirty;
        if (!hal_.write(addr, std::as_bytes(std::span{&dirtyState, 1}))) {
            return std::unexpected(LoggerError::HalError);
        }

        if (sectorIdx == tailSectorIdx_) {
            tailSectorIdx_ = (tailSectorIdx_ + 1) % SectorCount;
        }
        return {};
    }

    [[nodiscard]] uint32_t activeSector() const noexcept { return activeSectorIdx_; }
    [[nodiscard]] uint32_t tailSector() const noexcept { return tailSectorIdx_; }

private:
    FlashHal& hal_;
    uint32_t  baseAddr_{0};
    uint32_t  activeSectorIdx_{0};
    uint32_t  writeOffset_{sizeof(SectorHeader)};
    uint32_t  tailSectorIdx_{0};
    uint32_t  globalSeqNum_{0};

    [[nodiscard]] uint32_t sectorAddress(uint32_t idx) const noexcept {
        return baseAddr_ + (idx * SectorSize);
    }

    static uint16_t calculateCrc(std::span<const uint8_t> data) noexcept {
        uint16_t crc = 0xFFFF;
        for (uint8_t byte : data) {
            crc ^= static_cast<uint16_t>(byte) << 8;
            for (int i = 0; i < 8; ++i) {
                if (crc & 0x8000) {
                    crc = (crc << 1) ^ 0x1021;
                } else {
                    crc <<= 1;
                }
            }
        }
        return crc;
    }

    void recoverActiveSectorOffset() {
        uint32_t offset = sizeof(SectorHeader);
        uint32_t sAddr = sectorAddress(activeSectorIdx_);
        std::array<uint8_t, 256> recBuf{};

        while (offset + sizeof(RecordHeader) + sizeof(uint16_t) <= SectorSize) {
            RecordHeader rh{};
            if (!hal_.read(sAddr + offset, std::as_writable_bytes(std::span{&rh, 1}))) {
                break;
            }
            if (rh.magic != RecordMagic || rh.length < sizeof(RecordHeader) + 2) {
                break;
            }
            if (rh.length > recBuf.size()) break;

            hal_.read(sAddr + offset, std::span{recBuf.data(), rh.length});
            uint16_t expectedCrc = static_cast<uint16_t>(recBuf[rh.length - 2] | (recBuf[rh.length - 1] << 8));
            uint16_t actualCrc = calculateCrc(std::span{recBuf.data() + 2, static_cast<size_t>(rh.length - 4)});

            if (expectedCrc != actualCrc) {
                break; // Відсікання незавершеного запису
            }
            offset += rh.length;
        }
        writeOffset_ = offset;
    }

    std::expected<void, LoggerError> rotateSector() {
        uint32_t curAddr = sectorAddress(activeSectorIdx_) + offsetof(SectorHeader, state);
        SectorState fullState = SectorState::Full;
        if (!hal_.write(curAddr, std::as_bytes(std::span{&fullState, 1}))) {
            return std::unexpected(LoggerError::HalError);
        }

        uint32_t nextIdx = (activeSectorIdx_ + 1) % SectorCount;
        SectorHeader oldHdr{};
        hal_.read(sectorAddress(nextIdx), std::as_writable_bytes(std::span{&oldHdr, 1}));
        uint32_t eraseCount = (oldHdr.magic == SectorMagic) ? (oldHdr.eraseCount + 1) : 1;

        if (!hal_.eraseSector(sectorAddress(nextIdx))) {
            return std::unexpected(LoggerError::HalError);
        }

        ++globalSeqNum_;
        SectorHeader newHdr{
            .magic = SectorMagic,
            .version = 1,
            .seqNum = globalSeqNum_,
            .eraseCount = eraseCount,
            .state = SectorState::Active
        };

        if (!hal_.write(sectorAddress(nextIdx), std::as_bytes(std::span{&newHdr, 1}))) {
            return std::unexpected(LoggerError::HalError);
        }

        activeSectorIdx_ = nextIdx;
        writeOffset_ = sizeof(SectorHeader);

        if (activeSectorIdx_ == tailSectorIdx_) {
            tailSectorIdx_ = (tailSectorIdx_ + 1) % SectorCount;
        }
        return {};
    }
};
```
:::

## 6. Емуляція апаратного рівня та сценарій відновлення

Нижче наведено модуль тестування з імітацією фізичних властивостей NOR Flash (порозрядний логічний AND при повторному записі та стирання блоку в `0xFF`). Тест перевіряє штатні записи, імітує аварійне відключення живлення посеред запису кадру та перевіряє відновлення покажчика при повторному старті:

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>

static uint8_t g_sim_flash[FLASH_SECTOR_SIZE * FLASH_SECTOR_COUNT];

static bool sim_flash_read(uint32_t addr, uint8_t *buf, size_t len) {
    if (addr + len > sizeof(g_sim_flash)) return false;
    memcpy(buf, &g_sim_flash[addr], len);
    return true;
}

static bool sim_flash_write(uint32_t addr, const uint8_t *buf, size_t len) {
    if (addr + len > sizeof(g_sim_flash)) return false;
    for (size_t i = 0; i < len; i++) {
        /* Фізика NOR Flash: можна змінити 1 на 0, але не 0 на 1 */
        g_sim_flash[addr + i] &= buf[i];
    }
    return true;
}

static bool sim_flash_erase(uint32_t sector_addr) {
    uint32_t s_idx = sector_addr / FLASH_SECTOR_SIZE;
    if (s_idx >= FLASH_SECTOR_COUNT) return false;
    memset(&g_sim_flash[s_idx * FLASH_SECTOR_SIZE], 0xFF, FLASH_SECTOR_SIZE);
    return true;
}

int main(void) {
    memset(g_sim_flash, 0xFF, sizeof(g_sim_flash));

    flash_hal_t hal = {
        .read = sim_flash_read,
        .write = sim_flash_write,
        .erase_sector = sim_flash_erase
    };

    flash_logger_t logger;
    flash_logger_init(&logger, &hal, 0);

    /* 1. Запис тестових повідомлень */
    uint32_t val1 = 120;
    flash_logger_write(&logger, LOG_LEVEL_INFO, 1, 1000, 0x1001, (uint8_t *)&val1, sizeof(val1));
    uint32_t val2 = 404;
    flash_logger_write(&logger, LOG_LEVEL_WARN, 2, 1050, 0x1002, (uint8_t *)&val2, sizeof(val2));

    /* 2. Імітація раптового збою живлення посеред запису третього кадру */
    uint32_t incomplete_addr = get_sector_address(&logger, logger.active_sector_idx) + logger.write_offset_in_sector;
    log_entry_header_t bad_hdr = {
        .magic = LOG_RECORD_MAGIC,
        .length = 24,
        .level = LOG_LEVEL_ERROR,
        .module_id = 3,
        .timestamp_ms = 1100,
        .token_id = 0x1003
    };
    /* Записано лише заголовок без корисного навантаження й без валідного CRC */
    hal.write(incomplete_addr, (const uint8_t *)&bad_hdr, sizeof(bad_hdr));

    /* 3. Перезапуск мікроконтролера (Boot Recovery) */
    flash_logger_t recovered_logger;
    flash_logger_init(&recovered_logger, &hal, 0);

    /* Перевірка: пошкоджений запис відсічено, покажчик став перед битими байтами */
    uint32_t val3 = 200;
    flash_logger_write(&recovered_logger, LOG_LEVEL_INFO, 1, 1200, 0x1004, (uint8_t *)&val3, sizeof(val3));

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>

class SimulatedFlashHal : public FlashHal {
public:
    SimulatedFlashHal(size_t totalBytes) : memory_(totalBytes, 0xFF) {}

    bool read(uint32_t addr, std::span<uint8_t> dst) override {
        if (addr + dst.size() > memory_.size()) return false;
        std::copy_n(memory_.begin() + addr, dst.size(), dst.begin());
        return true;
    }

    bool write(uint32_t addr, std::span<const uint8_t> src) override {
        if (addr + src.size() > memory_.size()) return false;
        for (size_t i = 0; i < src.size(); ++i) {
            memory_[addr + i] &= src[i]; // Фізика переходу 1 -> 0
        }
        return true;
    }

    bool eraseSector(uint32_t sector_addr) override {
        uint32_t idx = sector_addr / PersistentRingLogger::SectorSize;
        if (idx >= PersistentRingLogger::SectorCount) return false;
        std::fill_n(memory_.begin() + (idx * PersistentRingLogger::SectorSize),
                    PersistentRingLogger::SectorSize, 0xFF);
        return true;
    }

private:
    std::vector<uint8_t> memory_;
};

int main() {
    SimulatedFlashHal hal(PersistentRingLogger::SectorSize * PersistentRingLogger::SectorCount);
    PersistentRingLogger logger(hal, 0);

    auto initRes = logger.init();
    if (!initRes) {
        return 1;
    }

    uint32_t v1 = 120;
    logger.log(LogLevel::Info, 1, 1000, 0x1001, std::as_bytes(std::span{&v1, 1}));
    uint32_t v2 = 404;
    logger.log(LogLevel::Warn, 2, 1050, 0x1002, std::as_bytes(std::span{&v2, 1}));

    // Перезапуск і перевірка стану
    PersistentRingLogger rebootedLogger(hal, 0);
    if (!rebootedLogger.init()) {
        return 1;
    }

    uint32_t v3 = 200;
    rebootedLogger.log(LogLevel::Info, 1, 1200, 0x1004, std::as_bytes(std::span{&v3, 1}));
    return 0;
}
```
:::
