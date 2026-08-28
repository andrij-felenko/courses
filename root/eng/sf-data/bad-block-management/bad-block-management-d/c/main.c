#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define NAND_PAGE_SIZE       4096u
#define NAND_OOB_SIZE        224u
#define NAND_PAGES_PER_BLOCK 64u
#define NAND_TOTAL_BLOCKS    1024u
#define NAND_RESERVED_BLOCKS 64u
#define NAND_USER_BLOCKS     (NAND_TOTAL_BLOCKS - NAND_RESERVED_BLOCKS)

#define OOB_MARKER_OFFSET    0u
#define GOOD_BLOCK_MARKER    0xFFu

typedef enum {
    BLOCK_FACTORY_BAD = 0x00,
    BLOCK_RESERVED    = 0x01,
    BLOCK_GROWN_BAD   = 0x02,
    BLOCK_GOOD        = 0x03
} bbt_state_t;

typedef struct {
    uint16_t bad_phys_block;
    uint16_t spare_phys_block;
    bool     active;
} remap_entry_t;

typedef struct {
    uint8_t       bbt_bitmap[NAND_TOTAL_BLOCKS / 4u]; // 2 біти на блок (256 байтів)
    remap_entry_t remap_table[NAND_RESERVED_BLOCKS];
    uint16_t      remap_count;
    uint16_t      next_free_reserved_idx;
} bbm_manager_t;

typedef struct {
    bool (*read_oob)(uint32_t block, uint32_t page, uint8_t *oob_buf);
    bool (*read_page)(uint32_t block, uint32_t page, uint8_t *data, uint8_t *oob);
    bool (*write_page)(uint32_t block, uint32_t page, const uint8_t *data, const uint8_t *oob);
    bool (*erase_block)(uint32_t block);
} nand_hw_ops_t;

static bbt_state_t bbm_get_state(const bbm_manager_t *mgr, uint16_t block) {
    if (block >= NAND_TOTAL_BLOCKS) return BLOCK_FACTORY_BAD;
    uint32_t byte_idx = block / 4u;
    uint32_t bit_shift = (block % 4u) * 2u;
    return (bbt_state_t)((mgr->bbt_bitmap[byte_idx] >> bit_shift) & 0x03u);
}

static void bbm_set_state(bbm_manager_t *mgr, uint16_t block, bbt_state_t state) {
    if (block >= NAND_TOTAL_BLOCKS) return;
    uint32_t byte_idx = block / 4u;
    uint32_t bit_shift = (block % 4u) * 2u;
    mgr->bbt_bitmap[byte_idx] &= ~(0x03u << bit_shift);
    mgr->bbt_bitmap[byte_idx] |= ((uint8_t)state & 0x03u) << bit_shift;
}

// Початкове сканування чипа та виявлення заводського браку
bool bbm_init_scan(bbm_manager_t *mgr, const nand_hw_ops_t *ops) {
    memset(mgr->bbt_bitmap, 0xFF, sizeof(mgr->bbt_bitmap));
    mgr->remap_count = 0;
    mgr->next_free_reserved_idx = NAND_USER_BLOCKS;

    uint8_t oob_buf[NAND_OOB_SIZE];

    for (uint16_t b = 0; b < NAND_TOTAL_BLOCKS; ++b) {
        bool is_bad = false;
        // Опитуємо першу (0) та другу (1) сторінки блоку
        for (uint32_t page = 0; page <= 1; ++page) {
            if (!ops->read_oob(b, page, oob_buf) || oob_buf[OOB_MARKER_OFFSET] != GOOD_BLOCK_MARKER) {
                is_bad = true;
                break;
            }
        }

        if (is_bad) {
            bbm_set_state(mgr, b, BLOCK_FACTORY_BAD);
        } else if (b >= NAND_USER_BLOCKS) {
            bbm_set_state(mgr, b, BLOCK_RESERVED);
        } else {
            bbm_set_state(mgr, b, BLOCK_GOOD);
        }
    }

    // Ремапінг виявлених дефектів у зоні користувача
    for (uint16_t b = 0; b < NAND_USER_BLOCKS; ++b) {
        if (bbm_get_state(mgr, b) == BLOCK_FACTORY_BAD) {
            while (mgr->next_free_reserved_idx < NAND_TOTAL_BLOCKS &&
                   bbm_get_state(mgr, mgr->next_free_reserved_idx) != BLOCK_RESERVED) {
                mgr->next_free_reserved_idx++;
            }
            if (mgr->next_free_reserved_idx >= NAND_TOTAL_BLOCKS) return false;

            uint16_t spare = mgr->next_free_reserved_idx++;
            mgr->remap_table[mgr->remap_count++] = (remap_entry_t){
                .bad_phys_block = b,
                .spare_phys_block = spare,
                .active = true
            };
        }
    }
    return true;
}

// Трансляція адреси користувача в реальний фізичний блок
uint16_t bbm_resolve_block(const bbm_manager_t *mgr, uint16_t user_block) {
    if (user_block >= NAND_USER_BLOCKS) return 0xFFFFu;

    if (bbm_get_state(mgr, user_block) == BLOCK_GOOD) {
        return user_block;
    }

    for (uint16_t i = 0; i < mgr->remap_count; ++i) {
        if (mgr->remap_table[i].active && mgr->remap_table[i].bad_phys_block == user_block) {
            return mgr->remap_table[i].spare_phys_block;
        }
    }
    return 0xFFFFu;
}
