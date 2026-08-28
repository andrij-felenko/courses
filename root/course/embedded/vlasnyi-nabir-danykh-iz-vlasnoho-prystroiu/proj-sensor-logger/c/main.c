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
