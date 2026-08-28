// Ядро Linux: linux/mmzone.h
typedef struct pglist_data {
    struct zone node_zones[MAX_NR_ZONES];
    struct zonelist node_zonelists[MAX_ZONELISTS];
    int nr_zones;
    
    unsigned long node_start_pfn;
    unsigned long node_present_pages;
    unsigned long node_spanned_pages;
    int node_id;
    
    wait_queue_head_t kswapd_wait;
    struct task_struct *kswapd;
    
    spinlock_t lru_lock;
    struct lruvec __lruvec;
} pg_data_t;
