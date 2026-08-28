#include <sched.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <cstdint>

struct sched_attr {
    std::uint32_t size;           // Розмір структури (sizeof(struct sched_attr))
    std::uint32_t sched_policy;   // SCHED_DEADLINE (6)
    std::uint64_t sched_flags;    // Додаткові прапорці (SCHED_FLAG_RESET_ON_FORK)
    std::int32_t  sched_nice;     // Використовується для SCHED_OTHER (-20..19)
    std::uint32_t sched_priority; // Використовується для SCHED_FIFO/RR (1..99)
    
    /* Параметри реального часу для SCHED_DEADLINE (у наносекундах) */
    std::uint64_t sched_runtime;  // Гарантований час виконання на період
    std::uint64_t sched_deadline; // Відносний дедлайн
    std::uint64_t sched_period;   // Період повторення завдання
};
