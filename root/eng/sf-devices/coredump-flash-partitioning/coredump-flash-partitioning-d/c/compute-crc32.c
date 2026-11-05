#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define COREDUMP_MAGIC_HEADER       0x434F5245U
#define COREDUMP_MAX_SLOTS          4U
#define COREDUMP_SLOT_SIZE          4096U
#define COREDUMP_PARTITION_BASE     0x08060000U /* Базова адреса Flash-розділу */

typedef enum {
    COREDUMP_STATE_ERASED     = 0xFFFFFFFFU,
    COREDUMP_STATE_START      = 0xFFFFFFFEU,
    COREDUMP_STATE_DATA_OK    = 0xFFFFFFFCU,
    COREDUMP_STATE_VALID      = 0xFFFFFFF8U,
    COREDUMP_STATE_EXTRACTED  = 0xFFFFFFF0U,
    COREDUMP_STATE_DIRTY      = 0x00000000U
} coredump_state_t;

typedef struct {
    uint32_t start_address;
    uint32_t length_bytes;
    uint32_t memory_type;
} memory_region_desc_t;

typedef struct {
    uint32_t magic;
    uint32_t state;
    uint32_t seq_num;
    uint64_t timestamp_ticks;
    uint32_t crash_reason_code;
    uint16_t arch_id;
    uint16_t num_regions;
    memory_region_desc_t regions[4];
    uint32_t header_crc;
} __attribute__((packed, aligned(4))) coredump_slot_header_t;

typedef struct {
    uint32_t r0, r1, r2, r3, r4, r5, r6, r7;
    uint32_t r8, r9, r10, r11, r12;
    uint32_t sp, lr, pc, xpsr;
    uint32_t cfsr, hfsr, mmar, bfar;
} __attribute__((packed, aligned(4))) coredump_cpu_context_t;

/* Обчислення контрольної суми CRC32 */
static uint32_t compute_crc32(const uint8_t *data, size_t length) {
    uint32_t crc = 0xFFFFFFFFU;
    for (size_t i = 0; i < length; ++i) {
        crc ^= (uint32_t)data[i];
        for (uint8_t bit = 0; bit < 8; ++bit) {
            uint32_t mask = -(crc & 1U);
            crc = (crc >> 1) ^ (0xEDB88320U & mask);
        }
    }
    return ~crc;
}

/* Верифікація цілісності збереженого слота */
static bool verify_slot_crc(uint32_t slot_addr) {
    const coredump_slot_header_t *hdr = (const coredump_slot_header_t *)slot_addr;
    if (hdr->magic != COREDUMP_MAGIC_HEADER || hdr->state != COREDUMP_STATE_VALID) {
        return false;
    }

    uint32_t running_crc = 0xFFFFFFFFU;
    uint32_t read_offset = sizeof(coredump_slot_header_t);

    /* 1. Додавання контексту процесора до CRC */
    const uint8_t *cpu_data = (const uint8_t *)(slot_addr + read_offset);
    for (size_t i = 0; i < sizeof(coredump_cpu_context_t); ++i) {
        running_crc ^= cpu_data[i];
        for (uint8_t b = 0; b < 8; ++b) {
            running_crc = (running_crc >> 1) ^ (0xEDB88320U & (-(running_crc & 1U)));
        }
    }
    read_offset += sizeof(coredump_cpu_context_t);

    /* 2. Додавання сегментів пам'яті до CRC */
    for (uint16_t r = 0; r < hdr->num_regions; ++r) {
        const uint8_t *reg_data = (const uint8_t *)(slot_addr + read_offset);
        for (size_t i = 0; i < hdr->regions[r].length_bytes; ++i) {
            running_crc ^= reg_data[i];
            for (uint8_t b = 0; b < 8; ++b) {
                running_crc = (running_crc >> 1) ^ (0xEDB88320U & (-(running_crc & 1U)));
            }
        }
        read_offset += hdr->regions[r].length_bytes;
    }
    running_crc = ~running_crc;

    uint32_t saved_crc = *(const uint32_t *)(slot_addr + read_offset);
    return (running_crc == saved_crc);
}

/* Функція пошуку найсвіжішого валідного аварійного дампу */
int32_t coredump_find_latest_valid_slot(uint32_t *out_slot_addr) {
    int32_t best_slot_idx = -1;
    uint32_t max_seq_num = 0;

    for (uint32_t i = 0; i < COREDUMP_MAX_SLOTS; ++i) {
        uint32_t slot_addr = COREDUMP_PARTITION_BASE + (i * COREDUMP_SLOT_SIZE);
        const coredump_slot_header_t *hdr = (const coredump_slot_header_t *)slot_addr;

        if (hdr->magic == COREDUMP_MAGIC_HEADER && hdr->state == COREDUMP_STATE_VALID) {
            if (verify_slot_crc(slot_addr)) {
                if (best_slot_idx == -1 || hdr->seq_num > max_seq_num) {
                    max_seq_num = hdr->seq_num;
                    best_slot_idx = (int32_t)i;
                    if (out_slot_addr) {
                        *out_slot_addr = slot_addr;
                    }
                }
            }
        }
    }
    return best_slot_idx;
}

/* Позначення слота як вичитаного після успішного вивантаження */
bool coredump_mark_slot_extracted(uint32_t slot_addr) {
    /* Зовнішня функція низькорівневого побайтового або пословного програмування Flash */
    extern bool flash_write_word(uint32_t address, uint32_t value);
    uint32_t state_addr = slot_addr + offsetof(coredump_slot_header_t, state);
    return flash_write_word(state_addr, COREDUMP_STATE_EXTRACTED);
}
