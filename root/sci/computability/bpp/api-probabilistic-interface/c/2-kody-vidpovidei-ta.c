/* c */
typedef enum {
    BPP_SUCCESS_ACCEPT     =  1, /* Слово належить мові (прийнято з гарантією 1 - eps) */
    BPP_SUCCESS_REJECT     =  0, /* Слово не належить мові (відхилено з гарантією 1 - eps) */
    BPP_ERROR_INVALID_PARAM = -1, /* Некоректні параметри (наприклад, eps >= 0.5) */
    BPP_ERROR_ENTROPY_FAIL = -2, /* Збій джерела випадкових чисел (виснаження ентропії) */
    BPP_ERROR_TIMEOUT      = -3  /* Перевищено часовий ліміт повторень */
} bpp_status_t;

typedef struct {
    uint32_t total_rounds_executed; /* Загальна кількість виконаних раундів k */
    uint32_t accept_votes;          /* Кількість раундів, що повернули 1 */
    uint32_t reject_votes;          /* Кількість раундів, що повернули 0 */
    double   estimated_error_bound; /* Обчислена верхня межа помилки за межею Чернова */
    uint64_t entropy_bytes_used;    /* Сумарний обсяг зчитаних випадкових байтів */
    uint64_t execution_time_us;     /* Час виконання у мікросекундах */
} bpp_execution_stats_t;
