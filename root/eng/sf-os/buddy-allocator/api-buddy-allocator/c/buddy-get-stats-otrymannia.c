typedef struct {
    size_t total_bytes;         /* Загальний обсяг керованого пулу */
    size_t free_bytes;          /* Сумарний обсяг вільної пам'яті в усіх списках */
    size_t allocated_bytes;     /* Сумарний обсяг пам'яті у зайнятих блоках */
    size_t free_blocks_count;   /* Кількість вільних блоків усіх порядків */
    size_t free_by_order[32];   /* Кількість вільних фрагментів окремо по кожному порядку */
} buddy_stats_t;

buddy_status_t buddy_get_stats(
    const buddy_allocator_t *alloc,
    buddy_stats_t           *stats
);
