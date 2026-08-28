struct pcstat_obj {
    struct list_head node;
    u32              payload;
};

struct pcstat_depot {
    local_lock_t     lock;
    struct list_head free;
    unsigned int     count;
};

static DEFINE_PER_CPU(struct pcstat_depot, pcstat_depot) = {
    .lock = INIT_LOCAL_LOCK(lock),
};

#define DEPOT_HIGH  16      /* більше не тримаємо — віддаємо розподілювачу */
#define DEPOT_WARM   4      /* стільки кладемо ядру процесора при вмиканні */
