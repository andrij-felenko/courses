struct em_perf_state {
    unsigned long frequency;   /* Робоча частота домену в кілогерцах (кГц) */
    unsigned long power;       /* Споживана потужність у міліватах (мВт) або мікроватах */
    unsigned long cost;        /* Обчислена вартість виконання = (power / performance) * 1024 */
    unsigned long flags;       /* Внутрішні прапорці стану (наприклад, EM_PERF_STATE_INEFFICIENT) */
};

struct em_perf_domain {
    struct em_perf_state *table; /* Масив станів OPP, відсортований за зростанням частоти */
    int nr_perf_states;          /* Кількість доступних станів OPP у масиві table */
    int flags;                   /* Прапорці домену (наприклад, EM_PERF_DOMAIN_MICROWATTS) */
    unsigned long cpus[1];       /* Бітова маска CPU, що входять до даного домену */
};
