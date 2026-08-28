# ⚙️ Надійний бінарний логер сенсорних потоків для мікроконтролера

Коли бортова нейромережа розробляється під реальний пристрій, збір сирих даних із давачів вимагає окремого програмного тракту, здатного гарантувати неперервність запису без жодної втрати вибірок (англ. *zero packet loss*). Звичайний наївний запис у файлову систему всередині циклу опитування сенсорів призводить до пропусків кадрів: накопичувачі Flash та картки SD мають непередбачувані затримки внутрішнього очищення блоків (англ. *Garbage Collection*), що можуть сягати 50–250 мілісекунд. Ця вставка розбирає закінчену архітектуру та еталонну реалізацію бінарного логера мовами C та C++ з подвійною буферизацією, виявленням випадання пакетів та апаратними часовими мітками.

### Чому наївний логер втрачає вибірки

Типова помилка розробника-початківця — виклик функції запису `f_write()` безпосередньо в обробнику переривання або в тілі основного циклу одразу після зчитування чергової вибірки з шини SPI чи I2C. На стенді в лабораторних умовах така схема створює ілюзію працездатності: більшість операцій запису у Flash-пам'ять займають від 1 до 3 мілісекунд, що цілком укладається в період опитування давачів на помірній частоті.

Проте фізична природа NAND Flash-пам'яті вимагає періодичного очищення застарілих сторінок цілими блоками (англ. *Erase Block*, розмір якого становить від 128 КБ до кількох мегабайтів). Коли внутрішній контролер SD-картки або мікросхеми eMMC запускає процедуру збирання сміття та вирівнювання зносу (англ. *Wear Leveling*), шина даних блокується на час до сотень мілісекунд. Якщо процесорний потік заблоковано на виклику запису, апаратний буфер FIFO в мікросхемі сенсора (який зазвичай вміщує лише від 16 до 32 вибірок) миттєво переповнюється, і нові вимірювання безповоротно втрачаються.

Щоб повністю розв'язати цю проблему в часі, логер розділяється на два незалежні шари:
1. **Високопріоритетний шар збору (Hard Real-Time):** таймери, DMA та швидкі переривання лише забирають сирі байти з апаратної периферії, маркують їх міткою часу та пакують у пам'ять RAM. Цей шар ніколи не виконує блокуючих викликів і не знає про існування файлової системи.
2. **Низькопріоритетний шар скидання (Background / Best-Effort):** окрема задача RTOS або фоновий обробник забирає повністю наповнені блоки пам'яті та передає їх драйверу накопичувача великими порціями, вирівняними за фізичним сектором носія (512 або 4096 байтів).

### Формат бінарного кадру

Текстові формати на зразок CSV є неприйнятними для бортового збору високочастотних даних: форматування чисел через `snprintf()` забирає сотні тактів процесора на кожне число, роздуває обсяг у 3–5 разів і робить неможливою пряму індексацію вибірок. Логер формує строго вирівняні бінарні кадри фіксованої структури:

```
[ Magic: 2B (0xAA55) ]
[ Stream ID: 1B ]
[ Flags: 1B ]
[ Sequence Number: 4B (uint32_t) ]
[ Hardware Timestamp: 8B (uint64_t, мікросекунди) ]
[ Payload Length: 2B (uint16_t) ]
[ Raw Payload: N байт ]
[ CRC32: 4B (контрольна сума) ]
```

Наявність поля `Sequence Number` дозволяє під час подальшої обробки на комп'ютері миттєво виявити, чи стався пропуск кадрів (`seq != prev_seq + 1`) і скільки саме вибірок було втрачено через переповнення черги. Поле `Timestamp` фіксує монотонний час з апаратного таймера мікроконтролера з точністю до мікросекунди, що унеможливлює накопичення часового дрейфу.

### Реалізація подвійної буферизації

Для ізоляції апаратного збору даних від повільного запису на накопичувач застосовується подвійний буфер (англ. *ping-pong buffer*). Поки DMA або швидкий обробник заповнює активний буфер `Buffer A`, фонова задача операційної системи (або головний цикл) записує попередньо наповнений `Buffer B` на диск блоками, кратними розміру сектора накопичувача.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define LOGGER_MAGIC        0xAA55
#define LOGGER_SECTOR_SIZE  512
#define LOGGER_PAYLOAD_MAX  240

typedef enum {
    STREAM_IMU_RAW      = 0x01,
    STREAM_CURRENT_ADC  = 0x02,
    STREAM_ACOUSTIC     = 0x03
} StreamId;

// Заголовок бінарного фрейму (18 байтів)
#pragma pack(push, 1)
typedef struct {
    uint16_t magic;
    uint8_t  stream_id;
    uint8_t  flags;
    uint32_t seq_num;
    uint64_t timestamp_us;
    uint16_t payload_len;
} LogFrameHeader;

typedef struct {
    LogFrameHeader header;
    uint8_t        payload[LOGGER_PAYLOAD_MAX];
    uint32_t       crc32;
} LogFrame;
#pragma pack(pop)

// Стан подвійного буфера
typedef struct {
    uint8_t  buffer[2][LOGGER_SECTOR_SIZE];
    uint32_t write_pos[2];
    volatile uint8_t active_idx;
    volatile bool    buffer_ready[2];
    uint32_t global_seq;
    uint32_t dropped_frames;
} DoubleBufferLogger;

// Швидкий розрахунок CRC32 (IEEE 802.3)
static uint32_t calculate_crc32(const uint8_t *data, size_t len) {
    uint32_t crc = 0xFFFFFFFF;
    for (size_t i = 0; i < len; ++i) {
        crc ^= data[i];
        for (int j = 0; j < 8; ++j) {
            crc = (crc >> 1) ^ (0xEDB88320 & (-(int32_t)(crc & 1)));
        }
    }
    return ~crc;
}

void logger_init(DoubleBufferLogger *logger) {
    memset(logger, 0, sizeof(DoubleBufferLogger));
    logger->active_idx = 0;
}

// Запис вибірки у високому пріоритеті (DMA / ISR / швидкий таймер)
bool logger_push_sample(DoubleBufferLogger *logger, StreamId stream,
                        uint64_t timestamp_us, const void *data, uint16_t len) {
    if (len > LOGGER_PAYLOAD_MAX) {
        return false;
    }

    uint8_t active = logger->active_idx;
    uint32_t frame_size = sizeof(LogFrameHeader) + len + sizeof(uint32_t);

    // Перевірка, чи влазить кадр у поточний буфер сектора
    if (logger->write_pos[active] + frame_size > LOGGER_SECTOR_SIZE) {
        // Поточний буфер заповнено, позначаємо його готовим до скидання
        logger->buffer_ready[active] = true;

        // Перемикаємось на протилежний буфер
        uint8_t next = active ^ 1;
        if (logger->buffer_ready[next]) {
            // Аварія: фоновий запис не встиг зберегти попередній буфер (затримка Flash)
            logger->dropped_frames++;
            return false;
        }

        logger->active_idx = next;
        logger->write_pos[next] = 0;
        active = next;
    }

    uint8_t *dest = &logger->buffer[active][logger->write_pos[active]];
    
    // Формуємо заголовок
    LogFrameHeader hdr;
    hdr.magic = LOGGER_MAGIC;
    hdr.stream_id = (uint8_t)stream;
    hdr.flags = 0;
    hdr.seq_num = logger->global_seq++;
    hdr.timestamp_us = timestamp_us;
    hdr.payload_len = len;

    memcpy(dest, &hdr, sizeof(LogFrameHeader));
    memcpy(dest + sizeof(LogFrameHeader), data, len);

    // Рахуємо контрольну суму заголовка та даних
    uint32_t crc = calculate_crc32(dest, sizeof(LogFrameHeader) + len);
    memcpy(dest + sizeof(LogFrameHeader) + len, &crc, sizeof(uint32_t));

    logger->write_pos[active] += frame_size;
    return true;
}

// Фонова функція скидання даних на SD-карту (викликається з низькопріоритетної задачі)
bool logger_flush_pending(DoubleBufferLogger *logger, 
                          bool (*storage_write_sector)(const uint8_t *sector, size_t bytes)) {
    for (uint8_t i = 0; i < 2; ++i) {
        if (logger->buffer_ready[i]) {
            // Запис вирівняного блоку на носій
            bool ok = storage_write_sector(logger->buffer[i], LOGGER_SECTOR_SIZE);
            if (ok) {
                logger->buffer_ready[i] = false;
                return true;
            }
            return false;
        }
    }
    return false;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <atomic>
#include <expected>
#include <algorithm>
#include <chrono>

enum class StreamId : uint8_t {
    ImuRaw      = 0x01,
    CurrentAdc  = 0x02,
    Acoustic    = 0x03
};

enum class LogError {
    PayloadTooLarge,
    BufferOverflow,
    StorageWriteFailed
};

#pragma pack(push, 1)
struct LogFrameHeader {
    uint16_t magic{0xAA55};
    StreamId stream_id{StreamId::ImuRaw};
    uint8_t  flags{0};
    uint32_t seq_num{0};
    uint64_t timestamp_us{0};
    uint16_t payload_len{0};
};
#pragma pack(pop)

template <size_t SectorSize = 512, size_t MaxPayload = 240>
class DoubleBufferLogger {
public:
    static constexpr uint16_t Magic = 0xAA55;

    DoubleBufferLogger() = default;

    // Запис вибірки у високому пріоритеті (без динамічного виділення пам'яті)
    std::expected<void, LogError> pushSample(
        StreamId stream,
        std::chrono::microseconds timestamp,
        std::span<const uint8_t> payload) noexcept 
    {
        if (payload.size() > MaxPayload) {
            return std::unexpected(LogError::PayloadTooLarge);
        }

        const uint8_t active = active_idx_.load(std::memory_order_relaxed);
        const size_t frame_size = sizeof(LogFrameHeader) + payload.size() + sizeof(uint32_t);

        if (write_pos_[active] + frame_size > SectorSize) {
            buffer_ready_[active].store(true, std::memory_order_release);

            const uint8_t next = active ^ 1;
            if (buffer_ready_[next].load(std::memory_order_acquire)) {
                dropped_frames_.fetch_add(1, std::memory_order_relaxed);
                return std::unexpected(LogError::BufferOverflow);
            }

            active_idx_.store(next, std::memory_order_relaxed);
            write_pos_[next] = 0;
            return writeFrameToBuffer(next, stream, timestamp, payload, frame_size);
        }

        return writeFrameToBuffer(active, stream, timestamp, payload, frame_size);
    }

    // Фонове скидання на диск через функціональний інтерфейс
    template <typename StorageWriter>
    std::expected<size_t, LogError> flushPending(StorageWriter&& writeSector) noexcept {
        size_t flushed_count = 0;
        for (size_t i = 0; i < 2; ++i) {
            if (buffer_ready_[i].load(std::memory_order_acquire)) {
                std::span<const uint8_t, SectorSize> sector_view(buffers_[i]);
                if (!writeSector(sector_view)) {
                    return std::unexpected(LogError::StorageWriteFailed);
                }
                buffer_ready_[i].store(false, std::memory_order_release);
                flushed_count++;
            }
        }
        return flushed_count;
    }

    [[nodiscard]] uint32_t droppedFrames() const noexcept {
        return dropped_frames_.load(std::memory_order_relaxed);
    }

private:
    std::expected<void, LogError> writeFrameToBuffer(
        uint8_t buf_idx,
        StreamId stream,
        std::chrono::microseconds timestamp,
        std::span<const uint8_t> payload,
        size_t frame_size) noexcept 
    {
        uint8_t* const dest = buffers_[buf_idx].data() + write_pos_[buf_idx];

        LogFrameHeader hdr{
            .magic = Magic,
            .stream_id = stream,
            .flags = 0,
            .seq_num = global_seq_++,
            .timestamp_us = static_cast<uint64_t>(timestamp.count()),
            .payload_len = static_cast<uint16_t>(payload.size())
        };

        std::copy_n(reinterpret_cast<const uint8_t*>(&hdr), sizeof(LogFrameHeader), dest);
        std::copy(payload.begin(), payload.end(), dest + sizeof(LogFrameHeader));

        const uint32_t crc = calculateCrc32(std::span<const uint8_t>(dest, sizeof(LogFrameHeader) + payload.size()));
        std::copy_n(reinterpret_cast<const uint8_t*>(&crc), sizeof(uint32_t), 
                    dest + sizeof(LogFrameHeader) + payload.size());

        write_pos_[buf_idx] += frame_size;
        return {};
    }

    static uint32_t calculateCrc32(std::span<const uint8_t> data) noexcept {
        uint32_t crc = 0xFFFFFFFF;
        for (const uint8_t byte : data) {
            crc ^= byte;
            for (int j = 0; j < 8; ++j) {
                crc = (crc >> 1) ^ (0xEDB88320 & (-(int32_t)(crc & 1)));
            }
        }
        return ~crc;
    }

    std::array<std::array<uint8_t, SectorSize>, 2> buffers_{};
    std::array<size_t, 2> write_pos_{0, 0};
    std::atomic<uint8_t> active_idx_{0};
    std::array<std::atomic<bool>, 2> buffer_ready_{false, false};
    uint32_t global_seq_{0};
    std::atomic<uint32_t> dropped_frames_{0};
};
```
:::

### Пастки реальної експлуатації логера

1. **Когерентність кешу на ядрах Cortex-M7.** Якщо буфери логера розташовано в кешованій області SRAM (D-Cache), а скидання на SD-карту виконується через SDIO/SPI DMA, ядро зобов'язане виконати очищення кешу даних (`SCB_CleanDCache_by_Addr`) перед стартом DMA-транзакції. Інакше контролер передасть застарілі дані з фізичної пам'яті замість оновлених рядків кешу, що призведе до запису пошкоджених секторів із невірними контрольними сумами.
2. **Вирівнювання пам'яті під DMA.** Більшість апаратних контролерів прямого доступу до пам'яті вимагають вирівнювання адрес буферів щонайменше за 4-байтовою (а для 32-байтних ліній кешу — 32-байтовою) межею. Використання вирівнювання `alignas(32)` гарантує відсутність апаратних відмов шини (англ. *Bus Fault*).
3. **Глибина черги під час затримок картки.** Якщо сенсор генерує сумарний потік 50 КБ/с, а картка пам'яті раптово підвисає на операцію стирання блоку Flash на 100 мс, у черзі накопичується 5 КБ даних. Двох секторів по 512 байтів у цьому випадку недостатньо — подвійний буфер переповниться вже через 10–20 мс. Для високошвидкісних потоків розмір кожного буфера збільшують до 4–16 КБ (кратних кластеру файлової системи), або організують кільцеву чергу з 8–16 секторних блоків.
4. **Атомарність закриття файлу при аварійному вимкненні.** Якщо живлення пристрою зникає посеред запису, таблиця файлової системи FatFS може залишитися в неконсистентному стані (розмір файлу дорівнюватиме нулю, хоча сектори вже записані). Щоб запобігти втраті цілих сесій випробувань, логер періодично виконує `f_sync()` або пише сирими секторами безпосередньо у виділений розділ Flash без файлової системи, а парсинг структури виконує утиліта на комп'ютері під час зчитування повного дампу носія.
