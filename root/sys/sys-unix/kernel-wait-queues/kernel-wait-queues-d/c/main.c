struct wait_queue_head {
    spinlock_t        lock;   /* захищає список */
    struct list_head  head;   /* двозв'язний список записів */
};

struct wait_queue_entry {
    unsigned int      flags;    /* WQ_FLAG_EXCLUSIVE, WQ_FLAG_WOKEN… */
    void             *private;  /* зазвичай — вказівник на task_struct охочого */
    wait_queue_func_t func;     /* що зробити, коли черга спрацює */
    struct list_head  entry;
};
