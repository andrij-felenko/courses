typedef struct buddy_allocator {
    uint8_t        *pool_base;        /* Початкова адреса керованого масиву пам'яті */
    size_t          pool_bytes;       /* Повний обсяг пулу у байтах (2^max_order) */
    uint8_t         min_order;        /* Логарифм мінімального розміру блоку */
    uint8_t         max_order;        /* Логарифм максимального розміру блоку */
    list_node_t     free_lists[32];   /* Голови циклічних списків вільних блоків зі сторожем */
    block_tag_t    *tags;             /* Зовнішній масив дескрипторів квантів */
    size_t          num_tags;         /* Кількість елементів у масиві tags */
    size_t          allocated_bytes;  /* Поточний обсяг пам'яті у виділених блоках */
    size_t          allocation_count; /* Лічильник успішно виконаних виділень */
} buddy_allocator_t;
