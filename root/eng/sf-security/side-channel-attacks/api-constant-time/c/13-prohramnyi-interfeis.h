typedef struct {
    double mean_fixed;
    double m2_fixed;
    uint64_t count_fixed;
    double mean_random;
    double m2_random;
    uint64_t count_random;
} ct_tvla_accumulator_t;

/* Ініціалізація структури статистичного збору */
void ct_tvla_init(ct_tvla_accumulator_t *acc);

/* Додавання вимірювання до вибірки (is_fixed == true для фіксованого класу) */
void ct_tvla_feed(ct_tvla_accumulator_t *acc, bool is_fixed, double metric_val);

/* Обчислення підсумкового значення статистики t-критерію Велча */
double ct_tvla_compute_t(const ct_tvla_accumulator_t *acc);

/* Перевірка, чи не перевищує статистика критичний поріг (дефолтний поріг 4.5) */
bool ct_tvla_is_leakage_free(const ct_tvla_accumulator_t *acc, double threshold);
