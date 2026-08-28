// Драйвер надійного запису кадру з контролем атомарності для C
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define RECORD_MAGIC   0x52454331  // "REC1"
#define COMMIT_FLAG    0xA55A5AA5

typedef struct __attribute__((packed)) {
    uint32_t magic;
    uint64_t seq_id;
    uint32_t payload_len;
} RecordHeader;

typedef struct __attribute__((packed)) {
    uint32_t crc32;
    uint32_t commit_flag;
} RecordFooter;

// Зовнішня функція апаратного розрахунку CRC32
extern uint32_t crc32_calculate(const uint8_t *data, size_t len);
extern uint32_t crc32_calculate_update(uint32_t crc, const uint8_t *data, size_t len);
extern bool flash_write_bytes(uint32_t addr, const uint8_t *data, size_t len);

bool record_write_atomic(uint32_t addr, uint64_t seq, const uint8_t *payload, uint32_t len) {
    RecordHeader hdr = {
        .magic = RECORD_MAGIC,
        .seq_id = seq,
        .payload_len = len
    };
    
    // 1. Запис заголовка
    if (!flash_write_bytes(addr, (const uint8_t*)&hdr, sizeof(hdr))) return false;
    uint32_t cur_addr = addr + sizeof(hdr);

    // 2. Запис корисного навантаження
    if (!flash_write_bytes(cur_addr, payload, len)) return false;
    cur_addr += len;

    // 3. Розрахунок CRC32 по заголовку та тілу
    uint32_t crc = crc32_calculate((const uint8_t*)&hdr, sizeof(hdr));
    crc = crc32_calculate_update(crc, payload, len);

    RecordFooter ftr = {
        .crc32 = crc,
        .commit_flag = 0xFFFFFFFF // поки не зафіксовано
    };
    if (!flash_write_bytes(cur_addr, (const uint8_t*)&ftr, sizeof(ftr))) return false;

    // 4. Фінальний атомарний комміт
    uint32_t commit = COMMIT_FLAG;
    return flash_write_bytes(cur_addr + offsetof(RecordFooter, commit_flag),
                             (const uint8_t*)&commit, sizeof(commit));
}
