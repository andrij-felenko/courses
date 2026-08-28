/* gc_sim.c — Симулятор збирання сміття у Flash на мові C */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>

#define PAGES_PER_BLOCK 64
#define TOTAL_BLOCKS    128
#define TOTAL_PAGES     (TOTAL_BLOCKS * PAGES_PER_BLOCK)

/* Резерв Over-Provisioning: 20% додаткових блоків */
#define HOST_LOGICAL_PAGES ((int)(TOTAL_PAGES * 0.80))

typedef enum {
    POLICY_GREEDY,
    POLICY_COST_BENEFIT
} gc_policy_t;

typedef struct {
    int valid_count;
    int invalid_count;
    int free_count;
    uint64_t last_write_time;
    uint32_t erase_count;
} block_meta_t;

typedef struct {
    int l2p[HOST_LOGICAL_PAGES];         /* LBA -> PPN */
    int p2l[TOTAL_PAGES];                /* PPN -> LBA */
    bool is_invalid[TOTAL_PAGES];        /* Прапор застарілості */
    block_meta_t blocks[TOTAL_BLOCKS];

    int active_block;
    int active_page_offset;

    uint64_t current_time;
    uint64_t host_writes;
    uint64_t nand_writes;
    uint64_t gc_copied_pages;
    uint64_t total_erases;
} ftl_sim_t;

static void ftl_init(ftl_sim_t *sim) {
    memset(sim, 0, sizeof(ftl_sim_t));
    for (int i = 0; i < HOST_LOGICAL_PAGES; i++) {
        sim->l2p[i] = -1;
    }
    for (int i = 0; i < TOTAL_PAGES; i++) {
        sim->p2l[i] = -1;
        sim->is_invalid[i] = false;
    }
    for (int b = 0; b < TOTAL_BLOCKS; b++) {
        sim->blocks[b].valid_count = 0;
        sim->blocks[b].invalid_count = 0;
        sim->blocks[b].free_count = PAGES_PER_BLOCK;
        sim->blocks[b].last_write_time = 0;
        sim->blocks[b].erase_count = 0;
    }
    sim->active_block = 0;
    sim->active_page_offset = 0;
}

static int count_free_blocks(const ftl_sim_t *sim) {
    int free_b = 0;
    for (int b = 0; b < TOTAL_BLOCKS; b++) {
        if (sim->blocks[b].free_count == PAGES_PER_BLOCK) {
            free_b++;
        }
    }
    return free_b;
}

static int get_next_free_block(ftl_sim_t *sim) {
    for (int b = 0; b < TOTAL_BLOCKS; b++) {
        if (b != sim->active_block && sim->blocks[b].free_count == PAGES_PER_BLOCK) {
            return b;
        }
    }
    return -1;
}

/* Обирає блок-жертву залежно від обраної політики */
static int select_victim_block(ftl_sim_t *sim, gc_policy_t policy) {
    int victim = -1;
    double best_score = -1.0;

    for (int b = 0; b < TOTAL_BLOCKS; b++) {
        if (b == sim->active_block) continue;
        block_meta_t *bm = &sim->blocks[b];
        if (bm->free_count == PAGES_PER_BLOCK) continue; /* Пропускаємо порожні */

        if (policy == POLICY_GREEDY) {
            /* Жадібна політика: шукаємо максимум застарілих сторінок (мінімум чинних) */
            double score = (double)bm->invalid_count;
            if (score > best_score) {
                best_score = score;
                victim = b;
            }
        } else if (policy == POLICY_COST_BENEFIT) {
            /* Політика Cost-Benefit: (1 - u) / (2 * u) * age */
            double u = (double)bm->valid_count / (double)PAGES_PER_BLOCK;
            if (u < 0.001) u = 0.001; /* Запобігання діленню на нуль */
            
            uint64_t age = sim->current_time - bm->last_write_time + 1;
            double score = ((1.0 - u) / (2.0 * u)) * (double)age;

            if (score > best_score) {
                best_score = score;
                victim = b;
            }
        }
    }
    return victim;
}

/* Виконання одного циклу збирання сміття */
static void run_gc(ftl_sim_t *sim, gc_policy_t policy) {
    int victim = select_victim_block(sim, policy);
    if (victim == -1) return;

    int new_target_block = get_next_free_block(sim);
    if (new_target_block == -1) return;

    int start_ppn = victim * PAGES_PER_BLOCK;
    int target_ppn_start = new_target_block * PAGES_PER_BLOCK;
    int target_offset = 0;

    /* 1. Евакуація чинних сторінок */
    for (int i = 0; i < PAGES_PER_BLOCK; i++) {
        int ppn = start_ppn + i;
        int lba = sim->p2l[ppn];

        if (lba != -1 && sim->l2p[lba] == ppn && !sim->is_invalid[ppn]) {
            /* Копіюємо чинну сторінку у новий блок */
            int new_ppn = target_ppn_start + target_offset++;
            sim->l2p[lba] = new_ppn;
            sim->p2l[new_ppn] = lba;
            sim->is_invalid[new_ppn] = false;
            sim->is_invalid[ppn] = true;

            sim->nand_writes++;
            sim->gc_copied_pages++;
            sim->blocks[new_target_block].valid_count++;
            sim->blocks[new_target_block].free_count--;
        }
    }

    sim->blocks[new_target_block].last_write_time = sim->current_time;

    /* 2. Стирання блоку-жертви */
    for (int i = 0; i < PAGES_PER_BLOCK; i++) {
        int ppn = start_ppn + i;
        sim->p2l[ppn] = -1;
        sim->is_invalid[ppn] = false;
    }
    sim->blocks[victim].valid_count = 0;
    sim->blocks[victim].invalid_count = 0;
    sim->blocks[victim].free_count = PAGES_PER_BLOCK;
    sim->blocks[victim].erase_count++;
    sim->total_erases++;
}

/* Запис сторінки від хоста */
static void ftl_write(ftl_sim_t *sim, int lba, gc_policy_t policy) {
    sim->current_time++;
    sim->host_writes++;

    /* Перевіряємо поріг вільних блоків для запуску GC */
    if (sim->blocks[sim->active_block].free_count == 0) {
        if (count_free_blocks(sim) < 3) {
            run_gc(sim, policy);
        }
        int next_b = get_next_free_block(sim);
        if (next_b != -1) {
            sim->active_block = next_b;
            sim->active_page_offset = 0;
        } else {
            /* Екстрений GC */
            run_gc(sim, policy);
            sim->active_block = get_next_free_block(sim);
            sim->active_page_offset = 0;
        }
    }

    /* Якщо LBA вже мав стару версію, позначаємо стару сторінку застарілою */
    int old_ppn = sim->l2p[lba];
    if (old_ppn != -1) {
        sim->is_invalid[old_ppn] = true;
        int old_b = old_ppn / PAGES_PER_BLOCK;
        sim->blocks[old_b].valid_count--;
        sim->blocks[old_b].invalid_count++;
    }

    /* Запис нової версії сторінки */
    int ppn = sim->active_block * PAGES_PER_BLOCK + sim->active_page_offset;
    sim->l2p[lba] = ppn;
    sim->p2l[ppn] = lba;
    sim->is_invalid[ppn] = false;

    sim->blocks[sim->active_block].valid_count++;
    sim->blocks[sim->active_block].free_count--;
    sim->blocks[sim->active_block].last_write_time = sim->current_time;
    sim->active_page_offset++;
    sim->nand_writes++;
}

int main(void) {
    printf("=== Симуляція Garbage Collection у Flash-сховищі ===\n\n");
    srand(42);

    gc_policy_t policies[2] = {POLICY_GREEDY, POLICY_COST_BENEFIT};
    const char *names[2] = {"Greedy (Жадібна)", "Cost-Benefit (Вартість/Вигода)"};

    for (int p = 0; p < 2; p++) {
        ftl_sim_t sim;
        ftl_init(&sim);

        /* Моделюємо 100 000 випадкових записів за законом Парето (80/20) */
        for (int i = 0; i < 100000; i++) {
            int lba;
            if ((rand() % 100) < 80) {
                lba = rand() % (HOST_LOGICAL_PAGES / 5);            /* Гаряча зона (20% LBA) */
            } else {
                lba = (HOST_LOGICAL_PAGES / 5) + 
                      rand() % (HOST_LOGICAL_PAGES - (HOST_LOGICAL_PAGES / 5)); /* Холодна зона */
            }
            ftl_write(&sim, lba, policies[p]);
        }

        double wa = (double)sim.nand_writes / (double)sim.host_writes;
        printf("--- Політика: %s ---\n", names[p]);
        printf("  Хостових записів:    %llu\n", (unsigned long long)sim.host_writes);
        printf("  Фізичних записів:    %llu\n", (unsigned long long)sim.nand_writes);
        printf("  Перенесено сторінок: %llu\n", (unsigned long long)sim.gc_copied_pages);
        printf("  Всього стирань:      %llu\n", (unsigned long long)sim.total_erases);
        printf("  Write Amplification (WA): %.3f\n\n", wa);
    }
    return 0;
}
