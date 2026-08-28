/**
 * @brief Обчислює дискретний логарифм x для рівняння g^x ≡ y (mod p).
 */
dlog_status_t dlog_solve_uint64(
    void *ctx,
    uint64_t g,
    uint64_t y,
    uint64_t p,
    uint64_t group_order,
    dlog_result_t *result
);
