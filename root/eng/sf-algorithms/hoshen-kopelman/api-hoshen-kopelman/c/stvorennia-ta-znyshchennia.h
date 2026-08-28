/* Створення контексту для обробки 2D ґратки */
hk_error_t hk_context_create_2d(
    hk_context_t** ctx_out,
    int width,
    int height,
    hk_connectivity_t connectivity,
    hk_boundary_t boundary
);

/* Звільнення всіх ресурсів контексту */
void hk_context_destroy(hk_context_t* ctx);

/* Очищення стану контексту для обробки нової ґратки тих самих розмірів */
hk_error_t hk_context_reset(hk_context_t* ctx);
