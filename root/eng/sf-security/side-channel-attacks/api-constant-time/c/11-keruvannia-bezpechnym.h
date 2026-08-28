typedef enum {
    CT_FLAG_NONE             = 0x00,
    CT_FLAG_SECURE_WIPE      = 0x01, /* Автоматичне занулення буферів при звільненні */
    CT_FLAG_LOCK_PAGES       = 0x02, /* Фіксація пам'яті в RAM (mlock) */
    CT_FLAG_DISABLE_COREDUMP = 0x04, /* Заборона створення дампів пам'яті процесу */
    CT_FLAG_BARRIER_STRICT   = 0x08  /* Примусова вставка асемблерних бар'єрів */
} ct_context_flags_t;

typedef struct {
    ct_context_flags_t flags;
    ct_rng_fn custom_rng;
    void *user_data;
} ct_context_t;

/* Ініціалізація криптографічного контексту */
int ct_context_init(ct_context_t *ctx, ct_context_flags_t flags, ct_rng_fn rng);

/* Звільнення ресурсів та деактивація контексту */
void ct_context_destroy(ct_context_t *ctx);

/* Виділення пам'яті з охоронними сторінками (Guard Pages) */
void *ct_alloc_guarded(ct_context_t *ctx, size_t size);

/* Звільнення захищеної пам'яті з гарантованим зануленням */
void ct_free_guarded(ct_context_t *ctx, void *ptr, size_t size);
