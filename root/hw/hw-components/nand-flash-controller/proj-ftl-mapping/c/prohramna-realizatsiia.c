#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define NUM_BLOCKS          8
#define PAGES_PER_BLOCK     8
#define TOTAL_PAGES         (NUM_BLOCKS * PAGES_PER_BLOCK)
#define LOGICAL_PAGES       32   // 100% Over-Provisioning для наочності
#define GC_THRESHOLD_BLOCKS 2
#define INVALID_ADDR        0xFFFFFFFF

typedef enum {
    PAGE_FREE = 0,
    PAGE_VALID = 1,
    PAGE_INVALID = 2
} page_state_t;

typedef struct {
    uint32_t erase_count;
    uint32_t valid_count;
    uint32_t invalid_count;
    uint32_t free_page_idx;
    page_state_t page_states[PAGES_PER_BLOCK];
    uint32_t page_lba[PAGES_PER_BLOCK];
} flash_block_t;

typedef struct {
    uint32_t l2p_table[LOGICAL_PAGES];
    flash_block_t blocks[NUM_BLOCKS];
    uint32_t active_block_id;
    uint64_t host_writes;
    uint64_t flash_writes;
} ftl_controller_t;

static void ftl_init(ftl_controller_t *ftl) {
    memset(ftl, 0, sizeof(*ftl));
    for (uint32_t i = 0; i < LOGICAL_PAGES; i++) {
        ftl->l2p_table[i] = INVALID_ADDR;
    }
    for (uint32_t b = 0; b < NUM_BLOCKS; b++) {
        for (uint32_t p = 0; p < PAGES_PER_BLOCK; p++) {
            ftl->blocks[b].page_lba[p] = INVALID_ADDR;
        }
    }
    ftl->active_block_id = 0;
}

static uint32_t ftl_count_free_blocks(const ftl_controller_t *ftl) {
    uint32_t free_cnt = 0;
    for (uint32_t b = 0; b < NUM_BLOCKS; b++) {
        if (b == ftl->active_block_id) continue;
        if (ftl->blocks[b].free_page_idx == 0 && ftl->blocks[b].valid_count == 0) {
            free_cnt++;
        }
    }
    return free_cnt;
}

static int32_t ftl_find_free_block(const ftl_controller_t *ftl) {
    for (uint32_t b = 0; b < NUM_BLOCKS; b++) {
        if (b == ftl->active_block_id) continue;
        if (ftl->blocks[b].free_page_idx == 0 && ftl->blocks[b].valid_count == 0) {
            return (int32_t)b;
        }
    }
    return -1;
}

static bool ftl_run_gc(ftl_controller_t *ftl) {
    int32_t victim_block = -1;
    uint32_t max_invalid = 0;

    // Пошук блоку-жертви за жадібною евристикою (Greedy Policy)
    for (uint32_t b = 0; b < NUM_BLOCKS; b++) {
        if (b == ftl->active_block_id) continue;
        if (ftl->blocks[b].free_page_idx == PAGES_PER_BLOCK &&
            ftl->blocks[b].invalid_count > max_invalid) {
            max_invalid = ftl->blocks[b].invalid_count;
            victim_block = (int32_t)b;
        }
    }

    if (victim_block < 0) return false;

    flash_block_t *victim = &ftl->blocks[victim_block];

    // Копіювання вцілілих дійсних сторінок у новий активний блок
    for (uint32_t p = 0; p < PAGES_PER_BLOCK; p++) {
        if (victim->page_states[p] == PAGE_VALID) {
            uint32_t lba = victim->page_lba[p];
            
            // Якщо в активному блоці закінчилося місце, відкриваємо наступний чистий
            if (ftl->blocks[ftl->active_block_id].free_page_idx == PAGES_PER_BLOCK) {
                int32_t next_b = ftl_find_free_block(ftl);
                if (next_b < 0) return false;
                ftl->active_block_id = (uint32_t)next_b;
            }

            flash_block_t *act = &ftl->blocks[ftl->active_block_id];
            uint32_t new_p = act->free_page_idx++;
            act->page_states[new_p] = PAGE_VALID;
            act->page_lba[new_p] = lba;
            act->valid_count++;

            // Оновлення таблиці трансляції L2P на нове фізичне зміщення
            ftl->l2p_table[lba] = (ftl->active_block_id * PAGES_PER_BLOCK) + new_p;
            ftl->flash_writes++;
        }
    }

    // Повне стирання блоку-жертви
    victim->erase_count++;
    victim->valid_count = 0;
    victim->invalid_count = 0;
    victim->free_page_idx = 0;
    for (uint32_t p = 0; p < PAGES_PER_BLOCK; p++) {
        victim->page_states[p] = PAGE_FREE;
        victim->page_lba[p] = INVALID_ADDR;
    }

    return true;
}

static bool ftl_write(ftl_controller_t *ftl, uint32_t lba) {
    if (lba >= LOGICAL_PAGES) return false;

    // Перевірка порогу пулу вільних блоків
    if (ftl_count_free_blocks(ftl) < GC_THRESHOLD_BLOCKS &&
        ftl->blocks[ftl->active_block_id].free_page_idx == PAGES_PER_BLOCK) {
        ftl_run_gc(ftl);
    }

    // Якщо поточний активний блок повністю заповнений, відкриваємо наступний
    if (ftl->blocks[ftl->active_block_id].free_page_idx == PAGES_PER_BLOCK) {
        int32_t free_b = ftl_find_free_block(ftl);
        if (free_b < 0) {
            if (!ftl_run_gc(ftl)) return false;
            free_b = ftl_find_free_block(ftl);
            if (free_b < 0) return false;
        }
        ftl->active_block_id = (uint32_t)free_b;
    }

    // Інвалідація старої фізичної сторінки (якщо цей LBA вже колись записувався)
    uint32_t old_pba = ftl->l2p_table[lba];
    if (old_pba != INVALID_ADDR) {
        uint32_t old_b = old_pba / PAGES_PER_BLOCK;
        uint32_t old_p = old_pba % PAGES_PER_BLOCK;
        ftl->blocks[old_b].page_states[old_p] = PAGE_INVALID;
        ftl->blocks[old_b].valid_count--;
        ftl->blocks[old_b].invalid_count++;
    }

    // Запис у наступну чисту сторінку активного блоку
    flash_block_t *act = &ftl->blocks[ftl->active_block_id];
    uint32_t new_p = act->free_page_idx++;
    act->page_states[new_p] = PAGE_VALID;
    act->page_lba[new_p] = lba;
    act->valid_count++;

    ftl->l2p_table[lba] = (ftl->active_block_id * PAGES_PER_BLOCK) + new_p;
    ftl->host_writes++;
    ftl->flash_writes++;

    return true;
}

int main(void) {
    ftl_controller_t ftl;
    ftl_init(&ftl);

    // Імітація 300 випадкових записів від операційної системи хоста
    for (int i = 0; i < 300; i++) {
        uint32_t random_lba = (uint32_t)(rand() % LOGICAL_PAGES);
        ftl_write(&ftl, random_lba);
    }

    printf("Результати симуляції FTL (C):\n");
    printf("  Хост-записів:     %lu\n", (unsigned long)ftl.host_writes);
    printf("  Флеш-записів:     %lu\n", (unsigned long)ftl.flash_writes);
    printf("  Розрахований WAF: %.3f\n", (double)ftl.flash_writes / (double)ftl.host_writes);

    return 0;
}
