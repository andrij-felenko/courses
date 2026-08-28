typedef enum {
    DEDUP_HASHSET,   // Дедуплікація через хеш-таблицю O(1)
    DEDUP_BLOOM,     // Ймовірнісна дедуплікація через фільтр Блума
    DEDUP_ARRAY      // Лінійний пошук O(N) у масиві (для малих систем)
} DedupPolicy;

typedef struct DovetailConfig {
    size_t initial_task_capacity; // Початкова ємність масиву задач (за замовчуванням 64)
    size_t initial_result_capacity; // Початкова ємність результатів (за замовчуванням 256)
    size_t memory_limit_bytes;   // Жорсткий ліміт пам'яті в байтах (0 = без обмежень)
    uint64_t max_diagonals;       // Гранична кількість діагоналей (0 = нескінченно)
    DedupPolicy dedup_policy;     // Політика перевірки унікальності
    bool enable_profiling;        // Прапорець збору метрик часу та промахів кешу
} DovetailConfig;
