#ifndef MEM_POOL_H
#define MEM_POOL_H

/*
 * Куча з обліком фрагментації.
 *
 * Штатний malloc відповідає лише на питання «скільки вільно всього», а
 * довгопрацюючий пристрій гине від іншого: вільного 20 КБ, але найбільший
 * суцільний блок — 1 КБ, і мережевий буфер виділити нікуди. Тому розподільник
 * веде адресно впорядкований список блоків і вміє назвати найбільший суцільний
 * вільний блок, а не лише суму.
 */

#include "budget_types.h"

typedef struct mem_block mem_block_t;

typedef struct {
    mem_block_t *head;         /* перший блок в адресному порядку */
    size_t       capacity;     /* корисна місткість пулу без заголовків */
    size_t       used_bytes;   /* сума розмірів зайнятих блоків */
    uint32_t     alloc_calls;
    uint32_t     free_calls;
    uint32_t     failed_calls; /* відмови у виділенні — головний сигнал біди */
} mem_pool_t;

typedef struct {
    size_t   capacity;
    size_t   used_bytes;
    size_t   free_bytes;        /* сумарний вільний обсяг */
    size_t   largest_free;      /* найбільший суцільний вільний блок */
    size_t   free_blocks;       /* кількість розривів у вільному просторі */
    uint32_t fragmentation_pm;  /* 1000 - largest/free, у проміле */
    uint32_t failed_calls;
} mem_pool_stats_t;

typedef struct {
    size_t min_free_bytes;    /* запас, нижче якого куча вважається вичерпаною */
    size_t min_largest_bytes; /* найбільший блок, потрібний найтовстішому буферу */
} mem_pool_limits_t;

/* Розмічає пул у наданому буфері. Буфер має пережити пул. */
bool mem_pool_init(mem_pool_t *pool, void *buffer, size_t size_bytes);

void *mem_pool_alloc(mem_pool_t *pool, size_t bytes);
void  mem_pool_free(mem_pool_t *pool, void *ptr);

void mem_pool_stats(const mem_pool_t *pool, mem_pool_stats_t *out);

budget_flags_t mem_pool_audit(const mem_pool_t *pool,
                              const mem_pool_limits_t *limits,
                              mem_pool_stats_t *stats);

#endif /* MEM_POOL_H */
