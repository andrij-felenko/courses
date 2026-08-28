/* Створення затиснутого дочірнього контексту для підзапиту */
bool create_subcall_context(const deadline_context_t *parent_ctx,
                            int64_t configured_subcall_timeout_ms,
                            int64_t min_viable_rtt_ms,
                            deadline_context_t *out_subcall_ctx) {
    int64_t parent_remain = context_remaining_ms(parent_ctx);

    /* Віднімаємо запас батьківського контексту */
    int64_t available = parent_remain - parent_ctx->safety_margin_ms;

    /* Якщо залишок менший за мінімальний мережевий RTT — підзапит безнадійний */
    if (available < min_viable_rtt_ms) {
        return false; /* Fail Fast: не робимо виклик */
    }

    /* Таймаут підзапиту — мінімум між конфігурацією та доступним залишком */
    int64_t subcall_timeout = configured_subcall_timeout_ms;
    if (subcall_timeout > available) {
        subcall_timeout = available;
    }

    *out_subcall_ctx = context_with_timeout(subcall_timeout, parent_ctx->safety_margin_ms);
    return true;
}
