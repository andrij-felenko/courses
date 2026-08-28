/* 1. Атомарний ланцюжок (захист через spinlock) */
struct atomic_notifier_head {
    spinlock_t lock;
    struct notifier_block *head;
};

/* 2. Блокуючий ланцюжок (захист через семафор читачів/письменників) */
struct blocking_notifier_head {
    struct rw_semaphore rwsem;
    struct notifier_block *head;
};

/* 3. Сирий ланцюжок (без внутрішніх блокувань) */
struct raw_notifier_head {
    struct notifier_block *head;
};

/* 4. SRCU-ланцюжок (Sleepable RCU) */
struct srcu_notifier_head {
    struct mutex mutex;
    struct srcu_struct srcu;
    struct notifier_block *head;
};
