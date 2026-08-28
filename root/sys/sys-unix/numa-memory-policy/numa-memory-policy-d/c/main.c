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
    
    /* Списки LRU для активних/неактивних сторінок вузла */
    struct lruvec __lruvec;
    
    /* Поля статистики та фонового вивільнення */
    unsigned long flags;
    struct per_cpu_nodestat __percpu *per_cpu_nodestats;
} pg_data_t;
