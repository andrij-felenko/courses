struct sched_attr {
    std::uint32_t size;           // Розмір структури для зворотної сумісності
    std::uint32_t sched_policy;   // Політика: SCHED_DEADLINE (значення 6)
    std::uint64_t sched_flags;    // Прапорці: SCHED_FLAG_RECLAIM тощо
    std::int32_t  sched_nice;     // Не використовується для DEADLINE
    std::uint32_t sched_priority; // Повинно бути 0 для DEADLINE
    
    // Параметри SCHED_DEADLINE (значення в наносекундах)
    std::uint64_t sched_runtime;  // Q: Бюджет виконання
    std::uint64_t sched_deadline; // D: Відносний дедлайн
    std::uint64_t sched_period;   // P: Період активації
};
