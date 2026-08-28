typedef struct {
    uint64_t truth_table_size;    /* Розмір N = 2^n бітів */
    uint64_t elapsed_time_us;     /* Фактичний час обчислення у мікросекундах */
    double estimated_largeness;   /* Обчислена частка випадкових функцій у C_n */
    int max_walsh_transform;      /* Максимальний абсолютний коефіцієнт Уолша */
    uint32_t algebraic_degree;    /* Алгебраїчний степінь булевої функції */
    bool is_constructive;         /* Прапорець задоволення умови Конструктивності */
    bool is_large;                /* Прапорець задоволення умови Великості */
    bool is_useful_against_poly;  /* Прапорець корисності проти класів P/poly */
    bool is_natural;              /* Підсумковий вердикт: чи є доведення Натуральним */
} natural_result_t;
