typedef struct {
    size_t initial_label_capacity; /* Початкова місткість масиву міток DSU (за замовчуванням 2048) */
    double growth_factor;          /* Коефіцієнт геометричного розширення місткості (1.5 - 2.0) */
    bool enable_simd;              /* Дозвіл використання векторних інструкцій AVX2 / NEON */
    bool compute_moments_on_fly;   /* Обчислення моментів другого порядку M_2 безпосередньо у першому проході */
    bool track_bounding_boxes;     /* Відстеження прямокутників обмеження (Bounding Box) для кожного кластера */
} hk_config_t;

/* Отримання конфігурації за замовчуванням */
void hk_config_init_default(hk_config_t* config);
