#include "mem_pool.h"

#include <string.h>

#define MEM_POOL_MAGIC 0x424C4B31u /* "BLK1" — захист від чужого вказівника */

struct mem_block {
    mem_block_t *next;
    mem_block_t *prev;
    size_t       size;  /* корисний розмір блоку, без заголовка */
    uint32_t     magic;
    bool         used;
};

#define MEM_ALIGN (sizeof(void *) * 2u)

static size_t align_up(size_t value, size_t alignment)
{
    return (value + alignment - 1u) & ~(alignment - 1u);
}

static size_t header_size(void)
{
    return align_up(sizeof(mem_block_t), MEM_ALIGN);
}

bool mem_pool_init(mem_pool_t *pool, void *buffer, size_t size_bytes)
{
    if (pool == NULL || buffer == NULL) {
        return false;
    }

    uintptr_t raw     = (uintptr_t)buffer;
    uintptr_t aligned = (uintptr_t)align_up((size_t)raw, MEM_ALIGN);
    size_t    skew    = (size_t)(aligned - raw);

    if (size_bytes <= skew) {
        return false;
    }
    size_bytes -= skew;

    const size_t hdr = header_size();
    if (size_bytes < hdr + MEM_ALIGN) {
        return false;
    }

    memset(pool, 0, sizeof *pool);

    mem_block_t *first = (mem_block_t *)aligned;
    first->next  = NULL;
    first->prev  = NULL;
    first->size  = size_bytes - hdr;
    first->magic = MEM_POOL_MAGIC;
    first->used  = false;

    pool->head     = first;
    pool->capacity = first->size;
    return true;
}

void *mem_pool_alloc(mem_pool_t *pool, size_t bytes)
{
    if (pool == NULL || pool->head == NULL || bytes == 0u) {
        return NULL;
    }

    const size_t hdr  = header_size();
    const size_t need = align_up(bytes, MEM_ALIGN);

    for (mem_block_t *b = pool->head; b != NULL; b = b->next) {
        if (b->used || b->size < need) {
            continue;
        }

        /* Хвіст відрізаємо лише тоді, коли з нього вийде корисний блок. */
        if (b->size >= need + hdr + MEM_ALIGN) {
            mem_block_t *tail = (mem_block_t *)((char *)b + hdr + need);
            tail->size  = b->size - need - hdr;
            tail->magic = MEM_POOL_MAGIC;
            tail->used  = false;
            tail->prev  = b;
            tail->next  = b->next;
            if (tail->next != NULL) {
                tail->next->prev = tail;
            }
            b->next = tail;
            b->size = need;
        }

        b->used = true;
        pool->used_bytes += b->size;
        pool->alloc_calls++;
        return (char *)b + hdr;
    }

    pool->failed_calls++;
    return NULL;
}

static bool block_belongs(const mem_pool_t *pool, const mem_block_t *block)
{
    for (const mem_block_t *b = pool->head; b != NULL; b = b->next) {
        if (b == block) {
            return true;
        }
    }
    return false;
}

void mem_pool_free(mem_pool_t *pool, void *ptr)
{
    if (pool == NULL || ptr == NULL) {
        return;
    }

    mem_block_t *b = (mem_block_t *)((char *)ptr - header_size());

    /* Чужий або вже звільнений вказівник не повинен рвати список. */
    if (b->magic != MEM_POOL_MAGIC || !b->used || !block_belongs(pool, b)) {
        return;
    }

    b->used = false;
    pool->used_bytes -= b->size;
    pool->free_calls++;

    /* Склеювання із сусідами — єдине, що стримує ріст фрагментації. */
    mem_block_t *next = b->next;
    if (next != NULL && !next->used) {
        b->size += header_size() + next->size;
        b->next = next->next;
        if (b->next != NULL) {
            b->next->prev = b;
        }
        next->magic = 0u;
    }

    mem_block_t *prev = b->prev;
    if (prev != NULL && !prev->used) {
        prev->size += header_size() + b->size;
        prev->next = b->next;
        if (prev->next != NULL) {
            prev->next->prev = prev;
        }
        b->magic = 0u;
    }
}

void mem_pool_stats(const mem_pool_t *pool, mem_pool_stats_t *out)
{
    if (out == NULL) {
        return;
    }
    memset(out, 0, sizeof *out);
    if (pool == NULL) {
        return;
    }

    for (const mem_block_t *b = pool->head; b != NULL; b = b->next) {
        if (b->used) {
            continue;
        }
        out->free_bytes += b->size;
        out->free_blocks++;
        if (b->size > out->largest_free) {
            out->largest_free = b->size;
        }
    }

    out->capacity     = pool->capacity;
    out->used_bytes   = pool->used_bytes;
    out->failed_calls = pool->failed_calls;

    if (out->free_bytes > 0u) {
        uint64_t ratio = (uint64_t)out->largest_free * 1000u / out->free_bytes;
        out->fragmentation_pm = (uint32_t)(1000u - ratio);
    }
}

budget_flags_t mem_pool_audit(const mem_pool_t *pool,
                              const mem_pool_limits_t *limits,
                              mem_pool_stats_t *stats)
{
    mem_pool_stats_t local;
    mem_pool_stats_t *s = (stats != NULL) ? stats : &local;
    mem_pool_stats(pool, s);

    if (limits == NULL) {
        return BUDGET_OK;
    }

    budget_flags_t flags = BUDGET_OK;
    if (s->free_bytes < limits->min_free_bytes) {
        flags |= BUDGET_HEAP_LOW;
    }
    /*
     * Окремий біт: вільного може вистачати з надлишком, але якщо найбільший
     * суцільний блок менший за найтовстіший буфер, наступне виділення впаде.
     */
    if (s->largest_free < limits->min_largest_bytes) {
        flags |= BUDGET_HEAP_FRAGMENTED;
    }
    return flags;
}
