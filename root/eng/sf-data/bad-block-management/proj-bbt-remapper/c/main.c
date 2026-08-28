#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define NAND_PAGE_SIZE       4096u
#define NAND_OOB_SIZE        224u
#define NAND_PAGES_PER_BLOCK 64u
#define NAND_TOTAL_BLOCKS    1024u
#define NAND_RESERVED_BLOCKS 64u
#define NAND_USER_BLOCKS     (NAND_TOTAL_BLOCKS - NAND_RESERVED_BLOCKS)

#define OOB_MARKER_OFFSET    0u      // Зміщення маркера браку в OOB
#define GOOD_BLOCK_MARKER    0xFFu
#define BBT_MAGIC_PRIMARY    0x42627430u // "Bbt0"
#define BBT_MAGIC_MIRROR     0x31746242u // "1tbB"

// 2-бітний стан блоку
typedef enum {
    BLOCK_FACTORY_BAD = 0x00,
    BLOCK_RESERVED    = 0x01,
    BLOCK_GROWN_BAD   = 0x02,
    BLOCK_GOOD        = 0x03
} bbt_state_t;

// Запис у таблиці перепризначення
typedef struct {
    uint16_t bad_phys_block;    // Фізичний блок з дефектом
    uint16_t spare_phys_block;  // Замінюючий блок із резервного пулу
    bool     active;
} remap_entry_t;

// Структура менеджера дефектних блоків
typedef struct {
    uint8_t       bbt_bitmap[NAND_TOTAL_BLOCKS / 4u]; // 2 біти на блок
    remap_entry_t remap_table[NAND_RESERVED_BLOCKS];
    uint16_t      remap_count;
    uint16_t      next_free_reserved_idx;
} bbm_manager_t;

// Апаратний інтерфейс низького рівня
typedef struct {
    bool (*read_oob)(uint32_t block, uint32_t page, uint8_t *oob_buf);
    bool (*read_page)(uint32_t block, uint32_t page, uint8_t *data, uint8_t *oob);
    bool (*write_page)(uint32_t block, uint32_t page, const uint8_t *data, const uint8_t *oob);
    bool (*erase_block)(uint32_t block);
} nand_hw_ops_t;

// Отримання 2-бітного стану блоку з бітової карти
static bbt_state_t bbm_get_state(const bbm_manager_t *mgr, uint16_t block) {
    if (block >= NAND_TOTAL_BLOCKS) return BLOCK_FACTORY_BAD;
    uint32_t byte_idx = block / 4u;
    uint32_t bit_shift = (block % 4u) * 2u;
    return (bbt_state_t)((mgr->bbt_bitmap[byte_idx] >> bit_shift) & 0x03u);
}

// Встановлення 2-бітного стану блоку
static void bbm_set_state(bbm_manager_t *mgr, uint16_t block, bbt_state_t state) {
    if (block >= NAND_TOTAL_BLOCKS) return;
    uint32_t byte_idx = block / 4u;
    uint32_t bit_shift = (block % 4u) * 2u;
    mgr->bbt_bitmap[byte_idx] &= ~(0x03u << bit_shift);
    mgr->bbt_bitmap[byte_idx] |= ((uint8_t)state & 0x03u) << bit_shift;
}

// Первинне сканування заводських маркерів у Spare Area
bool bbm_scan_factory_markers(bbm_manager_t *mgr, const nand_hw_ops_t *ops) {
    memset(mgr->bbt_bitmap, 0xFF, sizeof(mgr->bbt_bitmap)); // За замовчуванням всі GOOD
    mgr->remap_count = 0;
    mgr->next_free_reserved_idx = NAND_USER_BLOCKS;

    uint8_t oob_buf[NAND_OOB_SIZE];

    for (uint16_t b = 0; b < NAND_TOTAL_BLOCKS; ++b) {
        bool is_bad = false;
        // Перевіряємо сторінку 0 та сторінку 1
        for (uint32_t page = 0; page <= 1; ++page) {
            if (!ops->read_oob(b, page, oob_buf)) {
                is_bad = true;
                break;
            }
            if (oob_buf[OOB_MARKER_OFFSET] != GOOD_BLOCK_MARKER) {
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

    // Будуємо початкову таблицю перепризначень для дефектів у зоні користувача
    for (uint16_t b = 0; b < NAND_USER_BLOCKS; ++b) {
        if (bbm_get_state(mgr, b) == BLOCK_FACTORY_BAD) {
            while (mgr->next_free_reserved_idx < NAND_TOTAL_BLOCKS &&
                   bbm_get_state(mgr, mgr->next_free_reserved_idx) != BLOCK_RESERVED) {
                mgr->next_free_reserved_idx++;
            }
            if (mgr->next_free_reserved_idx >= NAND_TOTAL_BLOCKS) {
                return false; // Резервний пул вичерпано
            }
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

// Трансляція адреси користувача у реальний фізичний блок
uint16_t bbm_translate_address(const bbm_manager_t *mgr, uint16_t user_block) {
    if (user_block >= NAND_USER_BLOCKS) return 0xFFFFu;

    bbt_state_t state = bbm_get_state(mgr, user_block);
    if (state == BLOCK_GOOD) {
        return user_block; // Пряме відображення
    }

    for (uint16_t i = 0; i < mgr->remap_count; ++i) {
        if (mgr->remap_table[i].active && mgr->remap_table[i].bad_phys_block == user_block) {
            return mgr->remap_table[i].spare_phys_block;
        }
    }
    return 0xFFFFu; // Не знайдено заміни
}

// Динамічне виведення блоку з експлуатації при збої запису/стирання
bool bbm_retire_block_at_runtime(bbm_manager_t *mgr, const nand_hw_ops_t *ops,
                                 uint16_t failed_phys_block, uint32_t failed_page) {
    bbm_set_state(mgr, failed_phys_block, BLOCK_GROWN_BAD);

    while (mgr->next_free_reserved_idx < NAND_TOTAL_BLOCKS &&
           bbm_get_state(mgr, mgr->next_free_reserved_idx) != BLOCK_RESERVED) {
        mgr->next_free_reserved_idx++;
    }
    if (mgr->next_free_reserved_idx >= NAND_TOTAL_BLOCKS) {
        return false; // Немає вільних резервних блоків
    }
    uint16_t new_spare = mgr->next_free_reserved_idx++;

    if (!ops->erase_block(new_spare)) {
        bbm_set_state(mgr, new_spare, BLOCK_GROWN_BAD);
        return bbm_retire_block_at_runtime(mgr, ops, failed_phys_block, failed_page);
    }

    uint8_t data_buf[NAND_PAGE_SIZE];
    uint8_t oob_buf[NAND_OOB_SIZE];
    for (uint32_t p = 0; p < failed_page; ++p) {
        if (ops->read_page(failed_phys_block, p, data_buf, oob_buf)) {
            ops->write_page(new_spare, p, data_buf, oob_buf);
        }
    }

    bool updated = false;
    for (uint16_t i = 0; i < mgr->remap_count; ++i) {
        if (mgr->remap_table[i].spare_phys_block == failed_phys_block) {
            mgr->remap_table[i].spare_phys_block = new_spare;
            updated = true;
            break;
        }
    }
    if (!updated && mgr->remap_count < NAND_RESERVED_BLOCKS) {
        mgr->remap_table[mgr->remap_count++] = (remap_entry_t){
            .bad_phys_block = failed_phys_block,
            .spare_phys_block = new_spare,
            .active = true
        };
    }
    return true;
}
