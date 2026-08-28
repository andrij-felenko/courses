struct sched_attr {
    uint32_t size;              /* Розмір цієї структури в байтах (для розширюваності) */
    uint32_t sched_policy;      /* Політика планування (SCHED_OTHER, SCHED_BATCH, SCHED_IDLE, тощо) */
    uint64_t sched_flags;       /* Прапорці розширення (SCHED_FLAG_RESET_ON_FORK тощо) */
    int32_t  sched_nice;        /* Значення nice (-20..+19) для SCHED_OTHER та SCHED_BATCH */
    uint32_t sched_priority;    /* Статичний пріоритет (1..99 для RT; 0 для BATCH/IDLE/OTHER) */
    
    /* Поля для політики SCHED_DEADLINE (в наносекундах) */
    uint64_t sched_runtime;     /* Гарантований час виконання за період */
    uint64_t sched_deadline;    /* Відносний дедлайн */
    uint64_t sched_period;      /* Період виконання */
    
    /* Поля розширення ядра (Linux 5.3+) */
    uint32_t sched_util_min;    /* uclamp.min: мінімальна утилізація CPU */
    uint32_t sched_util_max;    /* uclamp.max: максимальна утилізація CPU */
};
