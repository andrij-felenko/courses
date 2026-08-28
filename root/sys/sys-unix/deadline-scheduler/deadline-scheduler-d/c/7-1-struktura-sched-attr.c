struct sched_attr {
    uint32_t size;              /* Розмір структури для зворотної сумісності */
    uint32_t sched_policy;      /* Політика: SCHED_DEADLINE (значення 6) */
    uint64_t sched_flags;       /* Прапорці: SCHED_FLAG_RECLAIM тощо */
    int32_t  sched_nice;        /* Не використовується для DEADLINE */
    uint32_t sched_priority;    /* Повинно бути 0 для DEADLINE */
    
    /* Параметри SCHED_DEADLINE (значення в наносекундах) */
    uint64_t sched_runtime;     /* Q: Бюджет виконання */
    uint64_t sched_deadline;    /* D: Відносний дедлайн */
    uint64_t sched_period;      /* P: Період активації */
};
