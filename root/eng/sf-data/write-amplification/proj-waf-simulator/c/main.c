#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>

#define PAGES_PER_BLOCK 16
#define USER_PAGES 64
#define TOTAL_BLOCKS 6
#define TOTAL_PHYSICAL_PAGES (TOTAL_BLOCKS * PAGES_PER_BLOCK)

typedef enum {
    PAGE_FREE,
    PAGE_VALID,
    PAGE_INVALID
} PageState;

typedef struct {
    PageState state;
    uint32_t lba;
} PhysicalPage;

typedef struct {
    PhysicalPage pages[PAGES_PER_BLOCK];
    uint32_t valid_count;
    uint32_t invalid_count;
    uint32_t free_count;
} EraseBlock;

typedef struct {
    EraseBlock blocks[TOTAL_BLOCKS];
    int32_t lba_table[USER_PAGES]; // LBA -> Physical Page Index (-1 if unmapped)
    uint32_t active_block;
    uint32_t active_page_idx;
    uint64_t host_writes;
    uint64_t gc_page_copies;
    uint64_t block_erases;
} FTLSimulator;

static void ftl_init(FTLSimulator *sim) {
    memset(sim, 0, sizeof(FTLSimulator));
    for (int i = 0; i < USER_PAGES; i++) {
        sim->lba_table[i] = -1;
    }
    for (int b = 0; b < TOTAL_BLOCKS; b++) {
        sim->blocks[b].free_count = PAGES_PER_BLOCK;
        for (int p = 0; p < PAGES_PER_BLOCK; p++) {
            sim->blocks[b].pages[p].state = PAGE_FREE;
            sim->blocks[b].pages[p].lba = 0;
        }
    }
    sim->active_block = 0;
    sim->active_page_idx = 0;
}

static int find_victim_block(const FTLSimulator *sim) {
    int victim = -1;
    uint32_t max_invalid = 0;
    for (int b = 0; b < TOTAL_BLOCKS; b++) {
        if (b == (int)sim->active_block) continue;
        if (sim->blocks[b].invalid_count > max_invalid) {
            max_invalid = sim->blocks[b].invalid_count;
            victim = b;
        }
    }
    return victim;
}

static void run_garbage_collection(FTLSimulator *sim) {
    int victim = find_victim_block(sim);
    if (victim < 0) return;

    EraseBlock *vblock = &sim->blocks[victim];
    
    // Перенесення живих сторінок
    for (int p = 0; p < PAGES_PER_BLOCK; p++) {
        if (vblock->pages[p].state == PAGE_VALID) {
            uint32_t lba = vblock->pages[p].lba;
            
            // Шукаємо вільне місце в активному блоці
            if (sim->active_page_idx >= PAGES_PER_BLOCK) {
                for (int b = 0; b < TOTAL_BLOCKS; b++) {
                    if (b != victim && sim->blocks[b].free_count == PAGES_PER_BLOCK) {
                        sim->active_block = b;
                        sim->active_page_idx = 0;
                        break;
                    }
                }
            }
            
            EraseBlock *ablock = &sim->blocks[sim->active_block];
            uint32_t pidx = sim->active_page_idx++;
            ablock->pages[pidx].state = PAGE_VALID;
            ablock->pages[pidx].lba = lba;
            ablock->free_count--;
            ablock->valid_count++;
            
            // Оновлюємо LBA таблицю
            sim->lba_table[lba] = (int32_t)(sim->active_block * PAGES_PER_BLOCK + pidx);
            sim->gc_page_copies++;
        }
    }
    
    // Стирання віктимного блоку
    for (int p = 0; p < PAGES_PER_BLOCK; p++) {
        vblock->pages[p].state = PAGE_FREE;
    }
    vblock->valid_count = 0;
    vblock->invalid_count = 0;
    vblock->free_count = PAGES_PER_BLOCK;
    sim->block_erases++;
}

static void ftl_write(FTLSimulator *sim, uint32_t lba) {
    if (lba >= USER_PAGES) return;
    
    if (sim->active_page_idx >= PAGES_PER_BLOCK || 
        sim->blocks[sim->active_block].free_count == 0) {
        run_garbage_collection(sim);
    }
    
    // Івалідація старої сторінки
    int32_t old_phys = sim->lba_table[lba];
    if (old_phys >= 0) {
        uint32_t old_block = old_phys / PAGES_PER_BLOCK;
        uint32_t old_page = old_phys % PAGES_PER_BLOCK;
        sim->blocks[old_block].pages[old_page].state = PAGE_INVALID;
        sim->blocks[old_block].valid_count--;
        sim->blocks[old_block].invalid_count++;
    }
    
    // Запис у новий блок
    EraseBlock *ablock = &sim->blocks[sim->active_block];
    uint32_t pidx = sim->active_page_idx++;
    ablock->pages[pidx].state = PAGE_VALID;
    ablock->pages[pidx].lba = lba;
    ablock->free_count--;
    ablock->valid_count++;
    
    sim->lba_table[lba] = (int32_t)(sim->active_block * PAGES_PER_BLOCK + pidx);
    sim->host_writes++;
}

int main(void) {
    FTLSimulator sim;
    ftl_init(&sim);
    
    printf("=== Симуляція FTL Garbage Collection та WAF (C) ===\n");
    
    srand(42);
    for (int i = 0; i < 1000; i++) {
        uint32_t lba = rand() % USER_PAGES;
        ftl_write(&sim, lba);
    }
    
    double waf = (double)(sim.host_writes + sim.gc_page_copies) / (double)sim.host_writes;
    
    printf("Записів від хоста (Host Writes): %llu сторінок\n", (unsigned long long)sim.host_writes);
    printf("Перенесень при GC (GC Page Copies): %llu сторінок\n", (unsigned long long)sim.gc_page_copies);
    printf("Стираннь блоків (Block Erases): %llu\n", (unsigned long long)sim.block_erases);
    printf("Разом записано на Flash: %llu сторінок\n", (unsigned long long)(sim.host_writes + sim.gc_page_copies));
    printf("Розрахований WAF: %.3f\n", waf);
    
    return 0;
}
