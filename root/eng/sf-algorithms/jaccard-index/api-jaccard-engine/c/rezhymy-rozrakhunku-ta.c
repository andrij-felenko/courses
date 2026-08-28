typedef enum {
    JACCARD_MODE_EXACT_SORTED = 0,
    JACCARD_MODE_EXACT_HASH   = 1,
    JACCARD_MODE_MINHASH      = 2
} jaccard_calc_mode_t;

typedef struct {
    jaccard_calc_mode_t mode; // Режим розрахунку схожості
    size_t shingle_size;      // Довжина k-грами у символах (за замовчуванням: 4)
    size_t minhash_k;         // Кількість хеш-функцій MinHash (за замовчуванням: 128)
    double sim_threshold;     // Порогове значення схожості τ ∈ (0, 1]
    uint64_t random_seed;     // Початкове зерно генератора випадкових чисел
} jaccard_config_t;
