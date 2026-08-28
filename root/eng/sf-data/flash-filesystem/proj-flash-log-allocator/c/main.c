#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>

#define FLASH_BLOCK_SIZE   4096
#define FLASH_BLOCK_COUNT  8
#define FLASH_MAGIC        0xA5

#define STATUS_COMMITTED   0x00
#define STATUS_INVALID     0x55
#define STATUS_EMPTY       0xFF

typedef enum {
    BLK_STATE_FREE = 0xFF,
    BLK_STATE_ACTIVE = 0xAA,
    BLK_STATE_FULL = 0x55
} block_state_t;

#pragma pack(push, 1)
typedef struct {
    uint8_t  magic;
    uint16_t record_id;
    uint16_t length;
    uint32_t sequence;
    uint8_t  status;       /* 0xFF: порожній, 0x00: зафіксовано, 0x55: застарілий */
    uint32_t crc32;
} record_header_t;

typedef struct {
    uint32_t erase_count;
    uint8_t  state;
    uint8_t  reserved[3];
} block_header_t;
#pragma pack(pop)

typedef struct {
    uint8_t raw[FLASH_BLOCK_COUNT][FLASH_BLOCK_SIZE];
    uint32_t global_seq;
    int active_block_idx;
    size_t write_offset;
} flash_engine_t;

/* Обчислення CRC32 для захисту від спотворення бітів */
static uint32_t compute_crc32(const uint8_t *data, size_t len) {
    uint32_t crc = 0xFFFFFFFF;
    for (size_t i = 0; i < len; i++) {
        crc ^= data[i];
        for (int j = 0; j < 8; j++) {
            if (crc & 1)
                crc = (crc >> 1) ^ 0xEDB88320;
            else
                crc >>= 1;
        }
    }
    return ~crc;
}

void flash_init(flash_engine_t *fe) {
    memset(fe->raw, 0xFF, sizeof(fe->raw));
    fe->global_seq = 1;
    fe->active_block_idx = -1;
    fe->write_offset = 0;

    for (int i = 0; i < FLASH_BLOCK_COUNT; i++) {
        block_header_t *bh = (block_header_t *)fe->raw[i];
        bh->erase_count = 0;
        bh->state = BLK_STATE_FREE;
    }
}

static bool flash_erase_block(flash_engine_t *fe, int block_idx) {
    if (block_idx < 0 || block_idx >= FLASH_BLOCK_COUNT) return false;
    block_header_t *bh = (block_header_t *)fe->raw[block_idx];
    uint32_t ec = bh->erase_count + 1;
    memset(fe->raw[block_idx], 0xFF, FLASH_BLOCK_SIZE);
    bh->erase_count = ec;
    bh->state = BLK_STATE_FREE;
    return true;
}

static int flash_allocate_free_block(flash_engine_t *fe) {
    int best_idx = -1;
    uint32_t min_erase = UINT32_MAX;

    /* Wear Leveling: виділяємо вільний блок із найменшим зносом */
    for (int i = 0; i < FLASH_BLOCK_COUNT; i++) {
        block_header_t *bh = (block_header_t *)fe->raw[i];
        if (bh->state == BLK_STATE_FREE && bh->erase_count < min_erase) {
            min_erase = bh->erase_count;
            best_idx = i;
        }
    }
    if (best_idx >= 0) {
        block_header_t *bh = (block_header_t *)fe->raw[best_idx];
        bh->state = BLK_STATE_ACTIVE;
    }
    return best_idx;
}

static int flash_select_gc_victim(flash_engine_t *fe) {
    int victim = -1;
    size_t max_obsolete_bytes = 0;

    for (int b = 0; b < FLASH_BLOCK_COUNT; b++) {
        if (b == fe->active_block_idx) continue;
        block_header_t *bh = (block_header_t *)fe->raw[b];
        if (bh->state != BLK_STATE_FULL) continue;

        size_t off = sizeof(block_header_t);
        size_t dead_bytes = 0;

        while (off + sizeof(record_header_t) <= FLASH_BLOCK_SIZE) {
            record_header_t *rh = (record_header_t *)&fe->raw[b][off];
            if (rh->magic != FLASH_MAGIC) break;
            if (rh->status == STATUS_INVALID) {
                dead_bytes += sizeof(record_header_t) + rh->length;
            }
            off += sizeof(record_header_t) + rh->length;
        }

        if (dead_bytes > max_obsolete_bytes) {
            max_obsolete_bytes = dead_bytes;
            victim = b;
        }
    }
    return victim;
}

bool flash_write_record(flash_engine_t *fe, uint16_t id, const uint8_t *payload, uint16_t len);

bool flash_run_gc(flash_engine_t *fe) {
    int victim = flash_select_gc_victim(fe);
    if (victim < 0) return false;

    size_t off = sizeof(block_header_t);
    while (off + sizeof(record_header_t) <= FLASH_BLOCK_SIZE) {
        record_header_t *rh = (record_header_t *)&fe->raw[victim][off];
        if (rh->magic != FLASH_MAGIC) break;

        if (rh->status == STATUS_COMMITTED) {
            const uint8_t *data = &fe->raw[victim][off + sizeof(record_header_t)];
            flash_write_record(fe, rh->record_id, data, rh->length);
        }
        off += sizeof(record_header_t) + rh->length;
    }

    flash_erase_block(fe, victim);
    return true;
}

static void flash_invalidate_prior_versions(flash_engine_t *fe, uint16_t id) {
    for (int b = 0; b < FLASH_BLOCK_COUNT; b++) {
        size_t off = sizeof(block_header_t);
        while (off + sizeof(record_header_t) <= FLASH_BLOCK_SIZE) {
            record_header_t *rh = (record_header_t *)&fe->raw[b][off];
            if (rh->magic != FLASH_MAGIC) break;
            if (rh->record_id == id && rh->status == STATUS_COMMITTED) {
                rh->status = STATUS_INVALID;
            }
            off += sizeof(record_header_t) + rh->length;
        }
    }
}

bool flash_write_record(flash_engine_t *fe, uint16_t id, const uint8_t *payload, uint16_t len) {
    size_t total_size = sizeof(record_header_t) + len;

    if (fe->active_block_idx < 0 || fe->write_offset + total_size > FLASH_BLOCK_SIZE) {
        if (fe->active_block_idx >= 0) {
            block_header_t *cur_bh = (block_header_t *)fe->raw[fe->active_block_idx];
            cur_bh->state = BLK_STATE_FULL;
        }

        int new_blk = flash_allocate_free_block(fe);
        if (new_blk < 0) {
            if (!flash_run_gc(fe)) return false;
            new_blk = flash_allocate_free_block(fe);
            if (new_blk < 0) return false;
        }

        fe->active_block_idx = new_blk;
        fe->write_offset = sizeof(block_header_t);
    }

    flash_invalidate_prior_versions(fe, id);

    record_header_t rh;
    rh.magic = FLASH_MAGIC;
    rh.record_id = id;
    rh.length = len;
    rh.sequence = fe->global_seq++;
    rh.status = STATUS_COMMITTED;
    rh.crc32 = compute_crc32(payload, len);

    uint8_t *dest = &fe->raw[fe->active_block_idx][fe->write_offset];
    memcpy(dest, &rh, sizeof(rh));
    memcpy(dest + sizeof(rh), payload, len);

    fe->write_offset += total_size;
    return true;
}

bool flash_read_record(const flash_engine_t *fe, uint16_t id, uint8_t *out_buf, uint16_t max_len, uint16_t *actual_len) {
    uint32_t best_seq = 0;
    const record_header_t *best_rh = NULL;
    const uint8_t *best_payload = NULL;

    for (int b = 0; b < FLASH_BLOCK_COUNT; b++) {
        size_t off = sizeof(block_header_t);
        while (off + sizeof(record_header_t) <= FLASH_BLOCK_SIZE) {
            const record_header_t *rh = (const record_header_t *)&fe->raw[b][off];
            if (rh->magic != FLASH_MAGIC) break;

            if (rh->record_id == id && rh->status == STATUS_COMMITTED && rh->sequence >= best_seq) {
                const uint8_t *payload = &fe->raw[b][off + sizeof(record_header_t)];
                if (compute_crc32(payload, rh->length) == rh->crc32) {
                    best_seq = rh->sequence;
                    best_rh = rh;
                    best_payload = payload;
                }
            }
            off += sizeof(record_header_t) + rh->length;
        }
    }

    if (!best_rh) return false;
    uint16_t to_copy = best_rh->length < max_len ? best_rh->length : max_len;
    memcpy(out_buf, best_payload, to_copy);
    if (actual_len) *actual_len = to_copy;
    return true;
}
