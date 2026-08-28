struct depot {
        local_lock_t     lock;
        struct list_head free;
};

/* статична ініціалізація */
static DEFINE_PER_CPU(struct depot, depot) = {
        .lock = INIT_LOCAL_LOCK(lock),
};

/* або на ходу */
local_lock_init(&depot.lock);
