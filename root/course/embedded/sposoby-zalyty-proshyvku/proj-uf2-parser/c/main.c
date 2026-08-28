#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define UF2_MAGIC_START0   0x0A324655UL  // "UF2\n"
#define UF2_MAGIC_START1   0x9E5D5157UL
#define UF2_MAGIC_END      0x0AB16414UL
#define UF2_FLAG_FAMILY_ID 0x00002000UL
#define UF2_BLOCK_SIZE     512
#define UF2_MAX_PAYLOAD    476

typedef enum {
    UF2_PARSE_OK = 0,
    UF2_ERR_NULL_PTR,
    UF2_ERR_BAD_MAGIC_START,
    UF2_ERR_BAD_MAGIC_END,
    UF2_ERR_FAMILY_MISMATCH,
    UF2_ERR_PAYLOAD_TOO_LARGE,
    UF2_ERR_INVALID_ADDRESS,
    UF2_ERR_TOTAL_BLOCKS_ZERO
} uf2_status_t;

typedef struct {
    uint32_t magic_start0;
    uint32_t magic_start1;
    uint32_t flags;
    uint32_t target_addr;
    uint32_t payload_size;
    uint32_t block_no;
    uint32_t num_blocks;
    uint32_t family_id;
    uint8_t  data[UF2_MAX_PAYLOAD];
    uint32_t magic_end;
} __attribute__((packed)) uf2_raw_block_t;

typedef struct {
    uint32_t target_address;
    uint32_t payload_length;
    uint32_t block_index;
    uint32_t total_blocks;
    const uint8_t *data_ptr;
} uf2_block_info_t;

uf2_status_t uf2_parse_and_validate_block(
    const uint8_t *sector_buf,
    uint32_t expected_family_id,
    uint32_t flash_start_addr,
    uint32_t flash_size_bytes,
    uf2_block_info_t *out_info
) {
    if (!sector_buf || !out_info) {
        return UF2_ERR_NULL_PTR;
    }

    const uf2_raw_block_t *blk = (const uf2_raw_block_t *)sector_buf;

    // Перевірка магічних сигнатур початку блоку
    if (blk->magic_start0 != UF2_MAGIC_START0 || blk->magic_start1 != UF2_MAGIC_START1) {
        return UF2_ERR_BAD_MAGIC_START;
    }

    // Перевірка магічної сигнатури кінця блоку
    if (blk->magic_end != UF2_MAGIC_END) {
        return UF2_ERR_BAD_MAGIC_END;
    }

    // Перевірка Family ID, якщо виставлено прапорець сімейства чіпа
    if ((blk->flags & UF2_FLAG_FAMILY_ID) != 0) {
        if (blk->family_id != expected_family_id) {
            return UF2_ERR_FAMILY_MISMATCH;
        }
    }

    // Перевірка ліміту корисного навантаження (типово 256 байт)
    if (blk->payload_size == 0 || blk->payload_size > UF2_MAX_PAYLOAD) {
        return UF2_ERR_PAYLOAD_TOO_LARGE;
    }

    if (blk->num_blocks == 0) {
        return UF2_ERR_TOTAL_BLOCKS_ZERO;
    }

    // Перевірка діапазону адрес Flash пам'яті
    uint32_t flash_end_addr = flash_start_addr + flash_size_bytes;
    if (blk->target_addr < flash_start_addr ||
        (blk->target_addr + blk->payload_size) > flash_end_addr) {
        return UF2_ERR_INVALID_ADDRESS;
    }

    out_info->target_address = blk->target_addr;
    out_info->payload_length = blk->payload_size;
    out_info->block_index = blk->block_no;
    out_info->total_blocks = blk->num_blocks;
    out_info->data_ptr = blk->data;

    return UF2_PARSE_OK;
}
