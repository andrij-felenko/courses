/* Формування HTTP-заголовка з залишком бюджету */
int serialize_deadline_header(const deadline_context_t *ctx, char *out_buf, size_t buf_size) {
    int64_t remain = context_remaining_ms(ctx);
    if (remain <= 0) {
        return -1; /* Бюджет вичерпано */
    }
    return snprintf(out_buf, buf_size, "X-Request-Deadline-Ms: %lld", (long long)remain);
}

/* Розбір заголовка на боці сервера та ініціалізація серверного контексту */
bool parse_deadline_header(const char *header_value, int64_t network_rtt_est_ms,
                           int64_t default_timeout_ms, deadline_context_t *out_ctx) {
    if (!header_value || *header_value == '\0') {
        /* Заголовка немає — застосовуємо дефолтний таймаут */
        *out_ctx = context_with_timeout(default_timeout_ms, 10);
        return true;
    }

    char *endptr = NULL;
    errno = 0;
    long long remain_ms = strtoll(header_value, &endptr, 10);
    if (errno != 0 || endptr == header_value || remain_ms <= 0) {
        return false;
    }

    /* Віднімаємо оцінку половини RTT на час польоту пакета */
    int64_t effective_remain = (int64_t)remain_ms - (network_rtt_est_ms / 2);
    if (effective_remain <= 0) {
        /* Запит летів довше, ніж жив дедлайн */
        out_ctx->deadline_ms = monotonic_now_ms();
        out_ctx->safety_margin_ms = 10;
        out_ctx->is_cancelled = true;
        return true;
    }

    out_ctx->deadline_ms = monotonic_now_ms() + effective_remain;
    out_ctx->safety_margin_ms = 10;
    out_ctx->is_cancelled = false;
    return true;
}
