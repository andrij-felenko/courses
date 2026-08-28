typedef struct pglist_data {
    struct zone node_zones[MAX_NR_ZONES];       // масив зон пам'яті (DMA, DMA32, Normal, Movable)
    struct zonelist node_zonelists[MAX_ZONELISTS]; // списки зон для пошуку вільної пам'яті при дефіциті
    int nr_zones;                               // кількість активних зон на цьому вузлі
    
    struct page *node_mem_map;                  // масив дескрипторів фізичних сторінок (struct page)
    unsigned long node_start_pfn;               // перший номер фізичного фрейму сторінки (Page Frame Number)
    unsigned long node_present_pages;           // реальна кількість присутніх сторінок
    unsigned long node_spanned_pages;           // загальний діапазон сторінок включно з дірками
    int node_id;                                // числовий номер NUMA-вузла (0, 1, ...)
    
    wait_queue_head_t kswapd_wait;              // черга очікування для фонового демона вивільнення kswapd
    struct task_struct *kswapd;                 // покажчик на потік ядра kswapd для даного вузла
    
    unsigned long min_unmapped_pages;           // поріг невідображених сторінок для zone_reclaim
    unsigned long min_slab_pages;               // поріг кешів SLAB для zone_reclaim
    
    CACHELINE_PADDING(_pad1_);
    spinlock_t lru_lock;                        // спінлок списків активних/неактивних сторінок (LRU)
    struct lruvec __lruvec;                     // списки сторінок LRU для алгоритмів заміщення
} pg_data_t;
