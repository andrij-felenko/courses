/* Структура для запису одного оракульного запиту */
typedef struct {
    uint64_t query_value;    /* Число, надіслане оракулу */
    bool answer;             /* Відповідь: true (1) / false (0) */
    uint64_t step_timestamp; /* Крок обчислення, на якому зроблено запит */
} otm_query_entry_t;

/* Протокол журналювання запитів */
typedef struct {
    otm_query_entry_t *entries;
    size_t count;
    size_t capacity;
    uint64_t max_queried_value; /* Значення u(x) - 1 */
} otm_query_trace_t;

/* Структура Провайдера Оракула */
typedef struct oracle_provider {
    oracle_type_t type;
    void *user_data;
    bool (*query_func)(struct oracle_provider *self, uint64_t val, otm_status_t *err);
    void (*free_func)(struct oracle_provider *self);
} oracle_provider_t;
