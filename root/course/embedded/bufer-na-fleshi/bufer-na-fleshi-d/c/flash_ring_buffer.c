/* flash_ring_buffer.c */
#include "flash_ring_buffer.h"
#include <string.h>

/* Проста еталонна реалізація CRC32 (IEEE 802.3) */
static uint32_t calc_crc32(const uint8_t *data, size_t len) {
    uint32_t crc = 0xFFFFFFFFU;
    for (size_t i = 0; i < len; i++) {
        crc ^= data[i];
        for (uint8_t j = 0; j < 8; j++) {
            crc = (crc >> 1) ^ (0xEDB88320U & (0 - (crc & 1)));
        }
    }
    return ~crc;
}

static uint32_t get_sector_addr(const flash_ring_t *ring, uint32_t sector_idx) {
    return ring->start_addr + (sector_idx * FLASH_SECTOR_SIZE);
}

/* Ініціалізація та сканування флешу для відновлення стану */
flash_ring_status_t flash_ring_init(flash_ring_t *ring, const flash_hal_t *hal, 
                                    uint32_t start_addr, uint32_t sector_count, 
                                    bool overwrite_on_full) {
    if (!ring || !hal || sector_count < 2) {
        return FLASH_RING_ERR_INVALID_PARAM;
    }

    ring->hal = *hal;
    ring->start_addr = start_addr;
    ring->sector_count = sector_count;
    ring->overwrite_on_full = overwrite_on_full;
    ring->next_record_seq = 1;
    ring->next_sector_seq = 1;

    uint32_t max_sec_seq = 0;
    uint32_t min_sec_seq = 0xFFFFFFFFU;
    int head_idx = -1;
    int tail_idx = -1;

    /* Фаза 1: Сканування заголовків усіх секторів */
    for (uint32_t i = 0; i < sector_count; i++) {
        flash_sector_hdr_t sec_hdr;
        uint32_t addr = get_sector_addr(ring, i);
        if (ring->hal.read(addr, (uint8_t*)&sec_hdr, sizeof(sec_hdr)) != 0) {
            return FLASH_RING_ERR_IO;
        }

        if (sec_hdr.magic == FLASH_SECTOR_MAGIC) {
            if (sec_hdr.sector_seq >= max_sec_seq) {
                max_sec_seq = sec_hdr.sector_seq;
                head_idx = (int)i;
            }
            if (sec_hdr.sector_seq <= min_sec_seq) {
                min_sec_seq = sec_hdr.sector_seq;
                tail_idx = (int)i;
            }
        }
    }

    /* Якщо жоден сектор не ініціалізовано — форматуємо сектор 0 */
    if (head_idx == -1) {
        ring->head_sector_idx = 0;
        ring->tail_sector_idx = 0;
        ring->head_offset = sizeof(flash_sector_hdr_t);
        ring->tail_offset = sizeof(flash_sector_hdr_t);

        ring->hal.erase_sector(get_sector_addr(ring, 0));
        flash_sector_hdr_t hdr = {
            .magic = FLASH_SECTOR_MAGIC,
            .sector_seq = 1,
            .state_flag = RECORD_STATUS_COMMITTED,
            .header_crc32 = 0
        };
        hdr.header_crc32 = calc_crc32((const uint8_t*)&hdr, sizeof(hdr) - 4);
        ring->hal.write_page(get_sector_addr(ring, 0), (const uint8_t*)&hdr, sizeof(hdr));
        ring->next_sector_seq = 2;
        return FLASH_RING_OK;
    }

    ring->head_sector_idx = (uint32_t)head_idx;
    ring->tail_sector_idx = (uint32_t)tail_idx;
    ring->next_sector_seq = max_sec_seq + 1;

    /* Фаза 2: Сканування Head-сектора для пошуку вільного зміщення */
    uint32_t cur_offset = sizeof(flash_sector_hdr_t);
    uint32_t head_base_addr = get_sector_addr(ring, ring->head_sector_idx);

    while (cur_offset + sizeof(flash_record_hdr_t) <= FLASH_SECTOR_SIZE) {
        flash_record_hdr_t rec;
        ring->hal.read(head_base_addr + cur_offset, (uint8_t*)&rec, sizeof(rec));

        if (rec.record_magic == 0xFFFFU && rec.status_flag == RECORD_STATUS_FREE) {
            /* Знайдено чисте місце для нових записів */
            break;
        }

        if (rec.record_magic == FLASH_RECORD_MAGIC) {
            if (rec.record_seq >= ring->next_record_seq) {
                ring->next_record_seq = rec.record_seq + 1;
            }
            cur_offset += sizeof(flash_record_hdr_t) + rec.payload_len;
        } else {
            /* Пошкоджений хвіст після знеструмлення — зупиняємо зміщення тут */
            break;
        }
    }
    ring->head_offset = cur_offset;
    ring->tail_offset = sizeof(flash_sector_hdr_t);

    return FLASH_RING_OK;
}

/* Додавання нового повідомлення в кільцевий буфер */
flash_ring_status_t flash_ring_push(flash_ring_t *ring, const uint8_t *payload, 
                                    uint16_t len, uint8_t priority) {
    if (!ring || !payload || len == 0) {
        return FLASH_RING_ERR_INVALID_PARAM;
    }

    uint32_t total_record_size = sizeof(flash_record_hdr_t) + len;
    if (total_record_size > (FLASH_SECTOR_SIZE - sizeof(flash_sector_hdr_t))) {
        return FLASH_RING_ERR_INVALID_PARAM; /* Повідомлення більше за вільний розмір сектора */
    }

    /* Перевірка: чи поміщається запис у поточний Head-сектор */
    if (ring->head_offset + total_record_size > FLASH_SECTOR_SIZE) {
        uint32_t next_head = (ring->head_sector_idx + 1) % ring->sector_count;

        /* Перевірка на переповнення кільця */
        if (next_head == ring->tail_sector_idx) {
            if (!ring->overwrite_on_full) {
                return FLASH_RING_ERR_FULL;
            }
            /* FIFO Drop: примусово зміщуємо Tail і стираємо найстаріший сектор */
            ring->tail_sector_idx = (ring->tail_sector_idx + 1) % ring->sector_count;
            ring->tail_offset = sizeof(flash_sector_hdr_t);
        }

        /* Підготовка нового сектора */
        ring->head_sector_idx = next_head;
        uint32_t sec_addr = get_sector_addr(ring, ring->head_sector_idx);
        ring->hal.erase_sector(sec_addr);

        flash_sector_hdr_t sec_hdr = {
            .magic = FLASH_SECTOR_MAGIC,
            .sector_seq = ring->next_sector_seq++,
            .state_flag = RECORD_STATUS_COMMITTED,
            .header_crc32 = 0
        };
        sec_hdr.header_crc32 = calc_crc32((const uint8_t*)&sec_hdr, sizeof(sec_hdr) - 4);
        ring->hal.write_page(sec_addr, (const uint8_t*)&sec_hdr, sizeof(sec_hdr));
        ring->head_offset = sizeof(flash_sector_hdr_t);
    }

    /* Формування заголовка запису зі статусом WRITING (0xFE) */
    flash_record_hdr_t rec_hdr = {
        .record_magic = FLASH_RECORD_MAGIC,
        .payload_len = len,
        .record_seq = ring->next_record_seq++,
        .status_flag = RECORD_STATUS_WRITING,
        .priority = priority,
        .reserved = 0,
        .payload_crc32 = calc_crc32(payload, len)
    };

    uint32_t rec_addr = get_sector_addr(ring, ring->head_sector_idx) + ring->head_offset;

    /* Запис заголовка та пейлоаду */
    ring->hal.write_page(rec_addr, (const uint8_t*)&rec_hdr, sizeof(rec_hdr));
    ring->hal.write_page(rec_addr + sizeof(rec_hdr), payload, len);

    /* Атомарний коміт: скидання статусу в 0xFC */
    uint8_t commit_val = RECORD_STATUS_COMMITTED;
    uint32_t status_addr = rec_addr + offsetof(flash_record_hdr_t, status_flag);
    ring->hal.write_page(status_addr, &commit_val, 1);

    ring->head_offset += total_record_size;
    return FLASH_RING_OK;
}

/* Підглядання (Peek) найстарішого непереданого повідомлення */
flash_ring_status_t flash_ring_peek(flash_ring_t *ring, uint8_t *payload_buf, 
                                    uint16_t max_buf_len, uint16_t *out_len, 
                                    uint32_t *out_record_seq) {
    if (!ring || !payload_buf || !out_len) {
        return FLASH_RING_ERR_INVALID_PARAM;
    }

    while (1) {
        if (ring->tail_sector_idx == ring->head_sector_idx && 
            ring->tail_offset >= ring->head_offset) {
            return FLASH_RING_ERR_EMPTY;
        }

        uint32_t rec_addr = get_sector_addr(ring, ring->tail_sector_idx) + ring->tail_offset;
        flash_record_hdr_t rec_hdr;
        ring->hal.read(rec_addr, (uint8_t*)&rec_hdr, sizeof(rec_hdr));

        /* Якщо сектор закінчився — переходимо до наступного сектора */
        if (rec_hdr.record_magic != FLASH_RECORD_MAGIC || 
            ring->tail_offset + sizeof(rec_hdr) > FLASH_SECTOR_SIZE) {
            if (ring->tail_sector_idx == ring->head_sector_idx) {
                return FLASH_RING_ERR_EMPTY;
            }
            ring->tail_sector_idx = (ring->tail_sector_idx + 1) % ring->sector_count;
            ring->tail_offset = sizeof(flash_sector_hdr_t);
            continue;
        }

        /* Якщо запис уже вичитаний (0x00) — пропускаємо його */
        if (rec_hdr.status_flag == RECORD_STATUS_CONSUMED) {
            ring->tail_offset += sizeof(flash_record_hdr_t) + rec_hdr.payload_len;
            continue;
        }

        /* Якщо запис валідний і зафіксований (0xFC) */
        if (rec_hdr.status_flag == RECORD_STATUS_COMMITTED) {
            if (rec_hdr.payload_len > max_buf_len) {
                return FLASH_RING_ERR_INVALID_PARAM;
            }

            ring->hal.read(rec_addr + sizeof(rec_hdr), payload_buf, rec_hdr.payload_len);

            /* Перевірка цілісності даних */
            uint32_t actual_crc = calc_crc32(payload_buf, rec_hdr.payload_len);
            if (actual_crc != rec_hdr.payload_crc32) {
                /* Отруйне повідомлення: помічаємо видаленим і йдемо далі */
                uint8_t consume_val = RECORD_STATUS_CONSUMED;
                ring->hal.write_page(rec_addr + offsetof(flash_record_hdr_t, status_flag), 
                                     &consume_val, 1);
                ring->tail_offset += sizeof(flash_record_hdr_t) + rec_hdr.payload_len;
                continue;
            }

            *out_len = rec_hdr.payload_len;
            if (out_record_seq) *out_record_seq = rec_hdr.record_seq;
            return FLASH_RING_OK;
        }

        /* Якщо статус WRITING (0xFE) або пошкоджений */
        ring->tail_offset += sizeof(flash_record_hdr_t) + rec_hdr.payload_len;
    }
}

/* Підтвердження успішного відправлення: маркування запису як CONSUMED */
flash_ring_status_t flash_ring_commit_pop(flash_ring_t *ring) {
    if (!ring) return FLASH_RING_ERR_INVALID_PARAM;

    uint32_t rec_addr = get_sector_addr(ring, ring->tail_sector_idx) + ring->tail_offset;
    flash_record_hdr_t rec_hdr;
    ring->hal.read(rec_addr, (uint8_t*)&rec_hdr, sizeof(rec_hdr));

    if (rec_hdr.record_magic == FLASH_RECORD_MAGIC) {
        uint8_t consumed = RECORD_STATUS_CONSUMED;
        ring->hal.write_page(rec_addr + offsetof(flash_record_hdr_t, status_flag), &consumed, 1);
        ring->tail_offset += sizeof(flash_record_hdr_t) + rec_hdr.payload_len;
        return FLASH_RING_OK;
    }

    return FLASH_RING_ERR_CORRUPTED;
}
