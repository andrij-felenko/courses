#include <string.h>
#include <stdint.h>
#include <stdbool.h>

#define AUDIT_RECORD_SIZE       128U
#define AUDIT_HASH_SIZE         32U
#define AUDIT_MAGIC_SYNC        0x41554454U
#define AUDIT_SECTOR_MAGIC      0x53454354U
#define AUDIT_SLOTS_PER_SECTOR  32U
#define AUDIT_DATA_SLOTS        31U

typedef enum {
    AUDIT_OK = 0,
    AUDIT_ERR_PARAM = -1,
    AUDIT_ERR_FLASH = -2,
    AUDIT_ERR_CORRUPT = -3,
    AUDIT_ERR_FULL = -4,
    AUDIT_ERR_INIT = -5
} audit_status_t;

typedef struct {
    uint32_t (*read)(uint32_t addr, uint8_t *buf, size_t len);
    uint32_t (*write_page)(uint32_t addr, const uint8_t *buf, size_t len);
    uint32_t (*erase_sector)(uint32_t sector_addr);
    uint32_t total_size;
    uint32_t sector_size;
} audit_hal_t;

#pragma pack(push, 1)
typedef struct {
    uint32_t magic;
    uint8_t  version;
    uint8_t  flags;
    uint8_t  exec_status;
    uint8_t  payload_len;
    uint64_t sequence_id;
    uint64_t timestamp_utc_ms;
    uint64_t operator_id;
    uint16_t command_id;
    uint8_t  subsystem_id;
    uint8_t  padding0;
    uint8_t  payload[32];
    uint8_t  prev_hash[32];
    uint8_t  record_hash[32];
} audit_record_t;
#pragma pack(pop)

/* Прототип криптографічного прискорювача SHA-256 */
extern void sha256_calculate(const uint8_t *data, size_t len, uint8_t *out_hash);

typedef struct {
    const audit_hal_t *hal;
    uint64_t current_seq;
    uint32_t active_sector_addr;
    uint32_t next_slot_idx;
    uint8_t  last_hash[AUDIT_HASH_SIZE];
    bool     is_ready;
} audit_engine_t;

audit_status_t audit_engine_init(audit_engine_t *eng, const audit_hal_t *hal) {
    if (!eng || !hal || hal->sector_size != 4096) {
        return AUDIT_ERR_PARAM;
    }
    eng->hal = hal;
    eng->current_seq = 0;
    eng->active_sector_addr = 0;
    eng->next_slot_idx = 1;
    memset(eng->last_hash, 0xAA, AUDIT_HASH_SIZE); /* Genesis Hash */

    /* Сканування секторів для знаходження активної голови */
    uint32_t total_sectors = hal->total_size / hal->sector_size;
    bool found_active = false;

    for (uint32_t i = 0; i < total_sectors; ++i) {
        uint32_t s_addr = i * hal->sector_size;
        audit_record_t first_slot;
        if (hal->read(s_addr, (uint8_t *)&first_slot, sizeof(first_slot)) != 0) {
            return AUDIT_ERR_FLASH;
        }

        if (first_slot.magic == AUDIT_SECTOR_MAGIC) {
            /* Сектор відкритий, шукаємо останній вільний слот */
            eng->active_sector_addr = s_addr;
            found_active = true;
            
            for (uint32_t slot = 1; slot <= AUDIT_DATA_SLOTS; ++slot) {
                audit_record_t rec;
                hal->read(s_addr + slot * AUDIT_RECORD_SIZE, (uint8_t *)&rec, sizeof(rec));
                if (rec.magic == AUDIT_MAGIC_SYNC) {
                    eng->current_seq = rec.sequence_id;
                    memcpy(eng->last_hash, rec.record_hash, AUDIT_HASH_SIZE);
                    eng->next_slot_idx = slot + 1;
                } else {
                    eng->next_slot_idx = slot;
                    break;
                }
            }
            break;
        }
    }

    if (!found_active) {
        /* Перший старт приладу: стираємо сектор 0 та ініціалізуємо заголовок */
        hal->erase_sector(0);
        audit_record_t hdr;
        memset(&hdr, 0xFF, sizeof(hdr));
        hdr.magic = AUDIT_SECTOR_MAGIC;
        hal->write_page(0, (const uint8_t *)&hdr, sizeof(hdr));
        eng->active_sector_addr = 0;
        eng->next_slot_idx = 1;
    }

    eng->is_ready = true;
    return AUDIT_OK;
}

audit_status_t audit_engine_record(
    audit_engine_t *eng,
    uint64_t timestamp_utc,
    uint64_t operator_id,
    uint16_t command_id,
    uint8_t subsystem_id,
    const uint8_t *payload,
    uint8_t payload_len,
    uint64_t *out_seq
) {
    if (!eng || !eng->is_ready) return AUDIT_ERR_INIT;
    if (payload_len > 32) return AUDIT_ERR_PARAM;

    /* Перевірка потреби ротації сектора */
    if (eng->next_slot_idx > AUDIT_DATA_SLOTS) {
        uint32_t next_sector = eng->active_sector_addr + eng->hal->sector_size;
        if (next_sector >= eng->hal->total_size) {
            next_sector = 0;
        }
        eng->hal->erase_sector(next_sector);
        
        audit_record_t hdr;
        memset(&hdr, 0xFF, sizeof(hdr));
        hdr.magic = AUDIT_SECTOR_MAGIC;
        hdr.sequence_id = eng->current_seq + 1;
        memcpy(hdr.prev_hash, eng->last_hash, AUDIT_HASH_SIZE);
        eng->hal->write_page(next_sector, (const uint8_t *)&hdr, sizeof(hdr));

        eng->active_sector_addr = next_sector;
        eng->next_slot_idx = 1;
    }

    audit_record_t rec;
    memset(&rec, 0, sizeof(rec));
    rec.magic = AUDIT_MAGIC_SYNC;
    rec.version = 1;
    rec.flags = 0;
    rec.exec_status = 0; /* PENDING */
    rec.payload_len = payload_len;
    rec.sequence_id = ++eng->current_seq;
    rec.timestamp_utc_ms = timestamp_utc;
    rec.operator_id = operator_id;
    rec.command_id = command_id;
    rec.subsystem_id = subsystem_id;
    
    if (payload && payload_len > 0) {
        memcpy(rec.payload, payload, payload_len);
    }
    memcpy(rec.prev_hash, eng->last_hash, AUDIT_HASH_SIZE);

    /* Розрахунок криптографічного хешу SHA-256 над першими 96 байтами */
    sha256_calculate((const uint8_t *)&rec, offsetof(audit_record_t, record_hash), rec.record_hash);

    /* Оновлення поточного хешу стану в ОЗП */
    memcpy(eng->last_hash, rec.record_hash, AUDIT_HASH_SIZE);

    /* Запис у відкритий слот Flash */
    uint32_t slot_addr = eng->active_sector_addr + (eng->next_slot_idx * AUDIT_RECORD_SIZE);
    if (eng->hal->write_page(slot_addr, (const uint8_t *)&rec, sizeof(rec)) != 0) {
        return AUDIT_ERR_FLASH;
    }

    eng->next_slot_idx++;
    if (out_seq) *out_seq = rec.sequence_id;

    return AUDIT_OK;
}
