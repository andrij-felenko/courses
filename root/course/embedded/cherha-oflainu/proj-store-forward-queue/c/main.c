#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define SF_MAGIC            0xAA55
#define SF_SECTOR_SIZE      4096
#define SF_PAGE_SIZE        256
#define SF_MAX_PAYLOAD      512

typedef enum {
    SF_PRIORITY_LOW = 0,    // Високочастотна телеметрія (50 Гц) — витісняється першою
    SF_PRIORITY_NORM = 1,   // Періодичний статус (1 Гц) — витісняється за чергою FIFO
    SF_PRIORITY_HIGH = 2,   // Аварійні сигнали та події — захищені від витіснення
} sf_priority_t;

#pragma pack(push, 1)
typedef struct {
    uint16_t magic;
    uint8_t  type;
    uint8_t  flags;
    uint32_t seq;
    uint64_t timestamp_ms;
    uint16_t payload_len;
    uint16_t reserved;
} sf_header_t;
#pragma pack(pop)

// Апаратна абстракція драйвера Flash
typedef struct {
    bool (*read)(uint32_t addr, uint8_t *buf, uint32_t size);
    bool (*write)(uint32_t addr, const uint8_t *buf, uint32_t size);
    bool (*erase_sector)(uint32_t sector_idx);
} sf_flash_driver_t;

typedef struct {
    sf_flash_driver_t drv;
    uint32_t base_addr;
    uint32_t sector_count;
    
    uint32_t head_sector;
    uint32_t head_offset;
    uint32_t tail_sector;
    uint32_t tail_offset;
    
    uint32_t next_seq;
    uint32_t unacked_seq;
    bool     is_full;
} sf_queue_t;

// Табличне обчислення CRC-32 (поліном IEEE 802.3 0xEDB88320)
uint32_t sf_crc32(const uint8_t *data, size_t len, uint32_t init_crc) {
    uint32_t crc = ~init_crc;
    while (len--) {
        crc ^= *data++;
        for (int k = 0; k < 8; k++) {
            crc = (crc >> 1) ^ (0xEDB88320U & (-(int32_t)(crc & 1)));
        }
    }
    return ~crc;
}

// Ініціалізація та сканування флеш-пам'яті при старті
bool sf_queue_init(sf_queue_t *q, const sf_flash_driver_t *drv, uint32_t base_addr, uint32_t sector_count) {
    q->drv = *drv;
    q->base_addr = base_addr;
    q->sector_count = sector_count;
    q->head_sector = 0;
    q->head_offset = 0;
    q->tail_sector = 0;
    q->tail_offset = 0;
    q->next_seq = 1;
    q->unacked_seq = 1;
    q->is_full = false;

    // Відновлення покажчика голови: сканування валідних записів у секторах
    uint32_t highest_seq = 0;
    uint32_t best_head_sec = 0;
    uint32_t best_head_off = 0;

    for (uint32_t s = 0; s < sector_count; s++) {
        uint32_t off = 0;
        while (off + sizeof(sf_header_t) <= SF_SECTOR_SIZE) {
            sf_header_t hdr;
            uint32_t phys_addr = base_addr + s * SF_SECTOR_SIZE + off;
            if (!q->drv.read(phys_addr, (uint8_t *)&hdr, sizeof(hdr))) {
                break;
            }

            if (hdr.magic != SF_MAGIC || hdr.payload_len > SF_MAX_PAYLOAD) {
                break; // Досягнуто чистої області 0xFF або кінця дійсних даних
            }

            uint32_t record_total = sizeof(sf_header_t) + hdr.payload_len + sizeof(uint32_t);
            if (off + record_total > SF_SECTOR_SIZE) {
                break;
            }

            // Перевірка цілісності запису за CRC-32
            uint8_t record_buf[sizeof(sf_header_t) + SF_MAX_PAYLOAD + sizeof(uint32_t)];
            if (q->drv.read(phys_addr, record_buf, record_total)) {
                uint32_t stored_crc;
                memcpy(&stored_crc, record_buf + record_total - sizeof(uint32_t), sizeof(uint32_t));
                uint32_t calc_crc = sf_crc32(record_buf, record_total - sizeof(uint32_t), 0);
                
                if (calc_crc == stored_crc) {
                    if (hdr.seq >= highest_seq) {
                        highest_seq = hdr.seq;
                        best_head_sec = s;
                        best_head_off = off + record_total;
                    }
                } else {
                    break; // CRC не зійшовся — наслідок знеструмлення під час запису
                }
            }
            off += record_total;
        }
    }

    if (highest_seq > 0) {
        q->head_sector = best_head_sec;
        q->head_offset = best_head_off;
        q->next_seq = highest_seq + 1;
    }

    return true;
}

// Запис нового кадру в чергу з випереджальним стиранням секторів
bool sf_queue_push(sf_queue_t *q, uint8_t type, sf_priority_t prio, uint64_t ts, const uint8_t *payload, uint16_t len) {
    if (len > SF_MAX_PAYLOAD) return false;

    uint32_t record_size = sizeof(sf_header_t) + len + sizeof(uint32_t);

    // Якщо новий запис не вміщується в поточний сектор — переходимо до наступного
    if (q->head_offset + record_size > SF_SECTOR_SIZE) {
        uint32_t next_sec = (q->head_sector + 1) % q->sector_count;
        
        // Перевірка на переповнення кільця
        if (next_sec == q->tail_sector) {
            if (prio == SF_PRIORITY_LOW) {
                // Відкидаємо низькопріоритетний шум, захищаючи історію від стирання
                return false;
            }
            // Для важливих даних зсуваємо хвіст (витісняємо найстаріший сектор)
            q->tail_sector = (q->tail_sector + 1) % q->sector_count;
            q->tail_offset = 0;
        }

        // Стирання нового сектора заздалегідь
        q->drv.erase_sector(next_sec);
        q->head_sector = next_sec;
        q->head_offset = 0;
    }

    // Формування структури заголовка
    sf_header_t hdr = {
        .magic = SF_MAGIC,
        .type = type,
        .flags = (uint8_t)prio,
        .seq = q->next_seq++,
        .timestamp_ms = ts,
        .payload_len = len,
        .reserved = 0
    };

    uint8_t buffer[sizeof(sf_header_t) + SF_MAX_PAYLOAD + sizeof(uint32_t)];
    memcpy(buffer, &hdr, sizeof(hdr));
    memcpy(buffer + sizeof(hdr), payload, len);

    uint32_t crc = sf_crc32(buffer, sizeof(hdr) + len, 0);
    memcpy(buffer + sizeof(hdr) + len, &crc, sizeof(crc));

    uint32_t write_addr = q->base_addr + q->head_sector * SF_SECTOR_SIZE + q->head_offset;
    if (q->drv.write(write_addr, buffer, record_size)) {
        q->head_offset += record_size;
        return true;
    }

    return false;
}

// Вибірка кадру з хвоста черги для передачі в мережу
bool sf_queue_peek_tail(sf_queue_t *q, sf_header_t *out_hdr, uint8_t *out_payload, uint32_t *out_record_size) {
    if (q->tail_sector == q->head_sector && q->tail_offset >= q->head_offset) {
        return false; // Черга порожня
    }

    uint32_t phys_addr = q->base_addr + q->tail_sector * SF_SECTOR_SIZE + q->tail_offset;
    if (!q->drv.read(phys_addr, (uint8_t *)out_hdr, sizeof(sf_header_t))) {
        return false;
    }

    if (out_hdr->magic != SF_MAGIC) {
        // Досягнуто кінця сектора — перехід до наступного сектора кільця
        q->tail_sector = (q->tail_sector + 1) % q->sector_count;
        q->tail_offset = 0;
        return false;
    }

    *out_record_size = sizeof(sf_header_t) + out_hdr->payload_len + sizeof(uint32_t);
    q->drv.read(phys_addr + sizeof(sf_header_t), out_payload, out_hdr->payload_len);
    return true;
}

// Підтвердження доставки порції даних сервером (ACK commit)
void sf_queue_commit_ack(sf_queue_t *q, uint32_t acked_seq) {
    while (q->tail_sector != q->head_sector || q->tail_offset < q->head_offset) {
        sf_header_t hdr;
        uint32_t phys_addr = q->base_addr + q->tail_sector * SF_SECTOR_SIZE + q->tail_offset;
        
        if (!q->drv.read(phys_addr, (uint8_t *)&hdr, sizeof(hdr)) || hdr.magic != SF_MAGIC) {
            q->tail_sector = (q->tail_sector + 1) % q->sector_count;
            q->tail_offset = 0;
            break;
        }

        if (hdr.seq <= acked_seq) {
            uint32_t rec_len = sizeof(sf_header_t) + hdr.payload_len + sizeof(uint32_t);
            q->tail_offset += rec_len;
            if (q->tail_offset + sizeof(sf_header_t) > SF_SECTOR_SIZE) {
                q->tail_sector = (q->tail_sector + 1) % q->sector_count;
                q->tail_offset = 0;
            }
        } else {
            break; // Дійшли до непідтверджених записів
        }
    }
}
