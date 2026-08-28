#include <sched.h>
#include <sys/syscall.h>
#include <unistd.h>

struct sched_attr {
    uint32_t size;              // Розмір структури (sizeof(struct sched_attr))
    uint32_t sched_policy;      // SCHED_DEADLINE (6)
    uint64_t sched_flags;       // Додаткові прапорці (SCHED_FLAG_RESET_ON_FORK)
    int32_t  sched_nice;        // Використовується для SCHED_OTHER (-20..19)
    uint32_t sched_priority;    // Використовується для SCHED_FIFO/RR (1..99)
    
    /* Параметри реального часу для SCHED_DEADLINE (у наносекундах) */
    uint64_t sched_runtime;     // Гарантований час виконання на період
    uint64_t sched_deadline;    // Відносний дедлайн
    uint64_t sched_period;      // Період повторення завдання
};
