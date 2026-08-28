struct wait_queue_head {
    spinlock_t        lock;   /* захищає список; беруть з вимкненням перервань */
    struct list_head  head;   /* двозв'язний список записів */
};

struct wait_queue_entry {
    unsigned int      flags;    /* WQ_FLAG_* */
    void             *private;  /* зазвичай task_struct того, хто чекає */
    wait_queue_func_t func;     /* що робити, коли чергу обходять */
    struct list_head  entry;
};

typedef int (*wait_queue_func_t)(struct wait_queue_entry *wq_entry,
                                 unsigned mode, int flags, void *key);
