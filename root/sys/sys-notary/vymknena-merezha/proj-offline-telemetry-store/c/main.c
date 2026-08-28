#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

/* Геометрія пам'яті NOR Flash */
#define FLASH_SECTOR_SIZE          4096U
#define FLASH_SECTOR_HEADER_SIZE   16U
#define FLASH_PAGE_SIZE            256U
#define FLASH_SECTOR_MAGIC         0x53464C53U  /* 'SFLS' */
#define FLASH_RECORD_MAGIC         0xAA55U

/* Стани секторів та записів */
#define FLASH_STATE_ERASED         0xFFU
#define FLASH_STATE_ALLOCATED      0xFEU
#define FLASH_STATE_COMMITTED      0xFCU
#define FLASH_STATE_DISPATCHED     0x00U

/* Заголовок сектора Flash (16 байтів) */
typedef struct __attribute__((packed)) {
    uint32_t magic;
    uint32_t sequence_num;
    uint32_t erase_count;
    uint8_t  state;
    uint8_t  reserved;
    uint16_t header_crc;
} flash_sector_header_t;

/* Структура датчиків телеметрії */
typedef struct {
    uint32_t timestamp;
    int32_t  temperature_c_x100; /* Температура * 100 (°C) */
    uint32_t pressure_pa;        /* Тиск у Паскалях */
    uint16_t battery_mv;         /* Напруга батареї в мВ */
    uint32_t pulse_count;        /* Лічильник імпульсів лічильника */
} telemetry_sample_t;

/* Апаратний інтерфейс драйвера SPI Flash (HAL) */
typedef struct {
    bool (*read)(uint32_t addr, uint8_t *buf, size_t size);
    bool (*write)(uint32_t addr, const uint8_t *buf, size_t size);
    bool (*erase_sector)(uint32_t sector_addr);
} flash_hal_t;

/* Контекст кільцевого буфера телеметрії */
typedef struct {
    const flash_hal_t *hal;
    uint32_t base_addr;
    uint32_t total_sectors;
    uint32_t head_sector_idx;
    uint32_t head_write_offset;
    uint32_t tail_sector_idx;
    uint32_t tail_read_offset;
    uint32_t global_seq_id;
    telemetry_sample_t last_sample;
    bool is_mounted;
} flash_ring_buffer_t;

/* Таблиця та обчислення CRC-32 (IEEE 802.3) */
static uint32_t crc32_update(uint32_t crc, const uint8_t *data, size_t len) {
    crc = ~crc;
    for (size_t i = 0; i < len; ++i) {
        crc ^= data[i];
        for (uint8_t j = 0; j < 8; ++j) {
            crc = (crc >> 1) ^ (0xEDB88320U & (-(crc & 1U)));
        }
    }
    return ~crc;
}

static uint16_t crc16_update(uint16_t crc, const uint8_t *data, size_t len) {
    for (size_t i = 0; i < len; ++i) {
        crc ^= (uint16_t)data[i] << 8;
        for (uint8_t j = 0; j < 8; ++j) {
            crc = (crc & 0x8000U) ? ((crc << 1) ^ 0x1021U) : (crc << 1);
        }
    }
    return crc;
}

/* Кодування ZigZag для знакового int32 */
static inline uint32_t zigzag_encode(int32_t val) {
    return (uint32_t)((val << 1) ^ (val >> 31));
}

static inline int32_t zigzag_decode(uint32_t val) {
    return (int32_t)((val >> 1) ^ (-(val & 1U)));
}

/* Кодування Varint у вихідний буфер */
static size_t varint_encode(uint32_t val, uint8_t *out) {
    size_t len = 0;
    while (val >= 0x80U) {
        out[len++] = (uint8_t)((val & 0x7FU) | 0x80U);
        val >>= 7;
    }
    out[len++] = (uint8_t)(val & 0x7FU);
    return len;
}

/* Декодування Varint із вхідного буфера */
static size_t varint_decode(const uint8_t *in, size_t max_len, uint32_t *val) {
    uint32_t res = 0;
    uint8_t shift = 0;
    size_t idx = 0;
    while (idx < max_len) {
        uint8_t byte = in[idx++];
        res |= (uint32_t)(byte & 0x7FU) << shift;
        if (!(byte & 0x80U)) {
            *val = res;
            return idx;
        }
        shift += 7;
        if (shift >= 35) return 0; /* Помилка формату */
    }
    return 0;
}

/* Упаковка дельт вимірювання */
static size_t compress_sample(const telemetry_sample_t *current,
                              const telemetry_sample_t *prev,
                              uint8_t *out_buf, size_t max_buf) {
    if (!current || !prev || !out_buf || max_buf < 32) return 0;

    size_t offset = 0;
    uint32_t dt = current->timestamp - prev->timestamp;
    int32_t d_temp = current->temperature_c_x100 - prev->temperature_c_x100;
    int32_t d_press = (int32_t)current->pressure_pa - (int32_t)prev->pressure_pa;
    int32_t d_volt = (int32_t)current->battery_mv - (int32_t)prev->battery_mv;
    uint32_t d_pulse = current->pulse_count - prev->pulse_count;

    offset += varint_encode(dt, &out_buf[offset]);
    offset += varint_encode(zigzag_encode(d_temp), &out_buf[offset]);
    offset += varint_encode(zigzag_encode(d_press), &out_buf[offset]);
    offset += varint_encode(zigzag_encode(d_volt), &out_buf[offset]);
    offset += varint_encode(d_pulse, &out_buf[offset]);

    return offset;
}

/* Ініціалізація та монтування кільцевого буфера */
bool flash_ring_buffer_mount(flash_ring_buffer_t *rb, const flash_hal_t *hal,
                             uint32_t base_addr, uint32_t total_sectors) {
    if (!rb || !hal || total_sectors < 2) return false;

    memset(rb, 0, sizeof(*rb));
    rb->hal = hal;
    rb->base_addr = base_addr;
    rb->total_sectors = total_sectors;

    uint32_t max_seq = 0;
    uint32_t min_seq = 0xFFFFFFFFU;
    bool found_active = false;

    /* Скан усіх секторів для пошуку Head та Tail */
    for (uint32_t i = 0; i < total_sectors; ++i) {
        flash_sector_header_t hdr;
        uint32_t addr = base_addr + (i * FLASH_SECTOR_SIZE);
        if (!hal->read(addr, (uint8_t *)&hdr, sizeof(hdr))) return false;

        uint16_t crc = crc16_update(0xFFFFU, (const uint8_t *)&hdr, 14);
        if (hdr.magic == FLASH_SECTOR_MAGIC && hdr.header_crc == crc) {
            found_active = true;
            if (hdr.sequence_num >= max_seq) {
                max_seq = hdr.sequence_num;
                rb->head_sector_idx = i;
            }
            if (hdr.state != FLASH_STATE_DISPATCHED && hdr.sequence_num <= min_seq) {
                min_seq = hdr.sequence_num;
                rb->tail_sector_idx = i;
            }
        }
    }

    if (!found_active) {
        /* Первинне форматування першого сектора */
        rb->head_sector_idx = 0;
        rb->tail_sector_idx = 0;
        rb->global_seq_id = 1;

        hal->erase_sector(base_addr);
        flash_sector_header_t new_hdr = {
            .magic = FLASH_SECTOR_MAGIC,
            .sequence_num = 1,
            .erase_count = 1,
            .state = FLASH_STATE_ALLOCATED,
            .reserved = 0xFFU,
            .header_crc = 0
        };
        new_hdr.header_crc = crc16_update(0xFFFFU, (const uint8_t *)&new_hdr, 14);
        hal->write(base_addr, (const uint8_t *)&new_hdr, sizeof(new_hdr));
        rb->head_write_offset = FLASH_SECTOR_HEADER_SIZE;
        rb->tail_read_offset = FLASH_SECTOR_HEADER_SIZE;
    } else {
        /* Знаходимо позицію голови запису в head_sector */
        uint32_t s_addr = base_addr + (rb->head_sector_idx * FLASH_SECTOR_SIZE);
        rb->head_write_offset = FLASH_SECTOR_HEADER_SIZE;

        while (rb->head_write_offset + 12 < FLASH_SECTOR_SIZE) {
            uint16_t rec_magic = 0;
            uint8_t rec_state = 0;
            uint16_t p_len = 0;
            hal->read(s_addr + rb->head_write_offset, (uint8_t *)&rec_magic, 2);

            if (rec_magic != FLASH_RECORD_MAGIC) break;

            hal->read(s_addr + rb->head_write_offset + 2, &rec_state, 1);
            hal->read(s_addr + rb->head_write_offset + 3, (uint8_t *)&p_len, 2);

            uint32_t total_rec_size = 2 + 1 + 2 + 4 + p_len + 4;
            if (rec_state == FLASH_STATE_COMMITTED) {
                rb->head_write_offset += total_rec_size;
            } else {
                /* Незавершений або пошкоджений запис — зупиняємося тут */
                break;
            }
        }
        rb->tail_read_offset = FLASH_SECTOR_HEADER_SIZE;
    }

    rb->is_mounted = true;
    return true;
}

/* Запис вимірювання у кільцевий буфер */
bool flash_ring_buffer_push(flash_ring_buffer_t *rb, const telemetry_sample_t *sample) {
    if (!rb || !rb->is_mounted || !sample) return false;

    uint8_t payload[64];
    size_t payload_len = compress_sample(sample, &rb->last_sample, payload, sizeof(payload));
    if (payload_len == 0) return false;

    uint32_t rec_total_size = 2 + 1 + 2 + 4 + (uint32_t)payload_len + 4;

    /* Перевіряємо, чи вміщується запис у поточний сектор */
    if (rb->head_write_offset + rec_total_size > FLASH_SECTOR_SIZE) {
        /* Закриваємо поточний сектор: встановлюємо стан 0xFC (FULL) */
        uint32_t cur_hdr_addr = rb->base_addr + (rb->head_sector_idx * FLASH_SECTOR_SIZE) + 12;
        uint8_t full_state = FLASH_STATE_COMMITTED;
        rb->hal->write(cur_hdr_addr, &full_state, 1);

        /* Переходимо до наступного сектора */
        uint32_t next_sector = (rb->head_sector_idx + 1) % rb->total_sectors;
        uint32_t next_addr = rb->base_addr + (next_sector * FLASH_SECTOR_SIZE);

        /* Зчитуємо лічильник зносу старого сектора */
        flash_sector_header_t old_hdr;
        rb->hal->read(next_addr, (uint8_t *)&old_hdr, sizeof(old_hdr));
        uint32_t er_cnt = (old_hdr.magic == FLASH_SECTOR_MAGIC) ? old_hdr.erase_count + 1 : 1;

        rb->hal->erase_sector(next_addr);

        flash_sector_header_t new_hdr = {
            .magic = FLASH_SECTOR_MAGIC,
            .sequence_num = ++rb->global_seq_id,
            .erase_count = er_cnt,
            .state = FLASH_STATE_ALLOCATED,
            .reserved = 0xFFU,
            .header_crc = 0
        };
        new_hdr.header_crc = crc16_update(0xFFFFU, (const uint8_t *)&new_hdr, 14);
        rb->hal->write(next_addr, (const uint8_t *)&new_hdr, sizeof(new_hdr));

        rb->head_sector_idx = next_sector;
        rb->head_write_offset = FLASH_SECTOR_HEADER_SIZE;
    }

    uint32_t write_addr = rb->base_addr + (rb->head_sector_idx * FLASH_SECTOR_SIZE) + rb->head_write_offset;

    /* 1. Записуємо маркер та початковий стан ALLOCATED (0xFE) */
    uint16_t magic = FLASH_RECORD_MAGIC;
    uint8_t state = FLASH_STATE_ALLOCATED;
    uint16_t len_field = (uint16_t)payload_len;
    uint32_t seq_id = rb->global_seq_id;

    rb->hal->write(write_addr, (const uint8_t *)&magic, 2);
    rb->hal->write(write_addr + 2, &state, 1);
    rb->hal->write(write_addr + 3, (const uint8_t *)&len_field, 2);
    rb->hal->write(write_addr + 5, (const uint8_t *)&seq_id, 4);

    /* 2. Записуємо стиснене корисне навантаження */
    rb->hal->write(write_addr + 9, payload, payload_len);

    /* 3. Обчислюємо та записуємо CRC-32 від seq_id та payload */
    uint32_t crc = crc32_update(0xFFFFFFFFU, (const uint8_t *)&seq_id, 4);
    crc = crc32_update(crc, payload, payload_len);
    rb->hal->write(write_addr + 9 + payload_len, (const uint8_t *)&crc, 4);

    /* 4. Фінальний атомарний коміт: переводимо стан у 0xFC (COMMITTED) */
    state = FLASH_STATE_COMMITTED;
    rb->hal->write(write_addr + 2, &state, 1);

    rb->head_write_offset += rec_total_size;
    rb->last_sample = *sample;
    return true;
}

/* Підтвердження успішного вивантаження батчу записів */
bool flash_ring_buffer_ack(flash_ring_buffer_t *rb, uint32_t sector_idx, uint32_t record_offset) {
    if (!rb || !rb->is_mounted || sector_idx >= rb->total_sectors) return false;

    uint32_t target_addr = rb->base_addr + (sector_idx * FLASH_SECTOR_SIZE) + record_offset + 2;
    uint8_t ack_state = FLASH_STATE_DISPATCHED; /* 0x00 */

    /* Записуємо 0x00 у байт стану запису */
    if (!rb->hal->write(target_addr, &ack_state, 1)) return false;

    /* Перевіряємо, чи всі записи в секторі мають стан DISPATCHED */
    uint32_t s_addr = rb->base_addr + (sector_idx * FLASH_SECTOR_SIZE);
    uint32_t off = FLASH_SECTOR_HEADER_SIZE;
    bool all_acked = true;

    while (off + 12 < FLASH_SECTOR_SIZE) {
        uint16_t rec_magic = 0;
        uint8_t rec_state = 0;
        uint16_t p_len = 0;
        rb->hal->read(s_addr + off, (uint8_t *)&rec_magic, 2);
        if (rec_magic != FLASH_RECORD_MAGIC) break;

        rb->hal->read(s_addr + off + 2, &rec_state, 1);
        rb->hal->read(s_addr + off + 3, (uint8_t *)&p_len, 2);

        if (rec_state != FLASH_STATE_DISPATCHED) {
            all_acked = false;
            break;
        }
        off += 2 + 1 + 2 + 4 + p_len + 4;
    }

    if (all_acked && sector_idx != rb->head_sector_idx) {
        /* Позначаємо весь сектор як DISPATCHED (0x00) */
        uint8_t sec_dispatched = FLASH_STATE_DISPATCHED;
        rb->hal->write(s_addr + 12, &sec_dispatched, 1);
        rb->tail_sector_idx = (sector_idx + 1) % rb->total_sectors;
    }

    return true;
}
