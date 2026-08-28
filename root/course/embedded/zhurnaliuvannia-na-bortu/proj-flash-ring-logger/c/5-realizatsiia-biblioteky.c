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
