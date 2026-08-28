typedef struct {
    ah_quantifier_kind_t kind; /* Тип квантора (EXISTS або FORALL) */
    char var_symbol[32];       /* Унікальний символьний ідентифікатор змінної */
    bool is_bounded;           /* Прапорець наявності верхньої межі (обмежений квантор) */
    uint64_t bound_limit;      /* Верхня межа діапазону [0, bound_limit] якщо is_bounded == true */
} ah_quantifier_t;

typedef struct {
    ah_class_type_t class_type;    /* Канонічний клас (SIGMA_N, PI_N, DELTA_N) */
    uint32_t level_n;             /* Кількість суворих чергувань кванторів (індекс n) */
    uint32_t oracle_jump_required;/* Номер оракульного стрибка 0^(n-1) */
    size_t raw_quantifier_count;  /* Початкова кількість кванторів у формулі */
    size_t contracted_count;      /* Кількість кванторів після згортання Кантора */
    bool is_decidable;            /* Чи є предикат повністю розв'язним без оракула (Δ₁⁰) */
    bool is_recursively_enumerable; /* Чи є предикат напіврозв'язним (Σ₁⁰) */
} ah_hierarchy_info_t;
