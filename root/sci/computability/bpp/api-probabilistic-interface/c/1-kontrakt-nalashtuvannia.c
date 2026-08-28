/* c */
typedef enum {
    BPP_MODE_FIXED_ROUNDS = 0, /* Фіксоване число раундів k */
    BPP_MODE_TARGET_ERROR  = 1  /* Автоматична ампліфікація до заданої хиби epsilon */
} bpp_amplification_mode_t;

typedef struct {
    bpp_amplification_mode_t mode;
    uint32_t                 rounds_k;      /* Кількість повторень (при BPP_MODE_FIXED_ROUNDS) */
    double                   max_error_eps; /* Максимальна допустима хиба (наприклад, 1e-12) */
    void*                    rng_context;   /* Контекст генератора випадкових чисел */
    uint64_t (*rng_next_u64)(void* ctx);    /* Функція вибірки 64 випадкових бітів */
} bpp_config_t;
