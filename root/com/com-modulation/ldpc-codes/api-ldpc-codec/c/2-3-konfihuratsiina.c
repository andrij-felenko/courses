typedef struct {
    uint32_t num_v;             /* Загальна довжина кодового слова n (кількість VN) */
    uint32_t num_c;             /* Кількість перевірочних рівнянь m (кількість CN) */
    const uint8_t *h_matrix;    /* Плоский масив розміру (num_c * num_v) елементів GF(2) */
    
    ldpc_algo_t algo;           /* Обраний алгоритм декодування */
    uint32_t max_iterations;    /* Максимальна кількість ітерацій (за замовчуванням 50) */
    float norm_factor;          /* Множник для Normalized Min-Sum (типово 0.8f) */
    float offset_factor;        /* Зміщення для Offset Min-Sum (типово 0.15f) */
    float llr_clip_val;         /* Поріг насичення LLR для запобігання переповненню (типово 20.0f) */
} ldpc_config_t;
