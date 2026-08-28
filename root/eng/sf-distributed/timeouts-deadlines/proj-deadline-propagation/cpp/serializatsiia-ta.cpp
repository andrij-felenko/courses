/* Формування значення заголовка з залишком часу */
std::optional<std::string> serialize_deadline(const DeadlineContext& ctx) {
    const auto rem = ctx.remaining().count();
    if (rem <= 0) {
        return std::nullopt;
    }
    return std::to_string(rem);
}

/* Розбір заголовка на сервері та побудова контексту */
std::optional<DeadlineContext> parse_deadline(std::string_view header_val,
                                             std::chrono::milliseconds rtt_estimate,
                                             std::chrono::milliseconds default_timeout) {
    if (header_val.empty()) {
        return DeadlineContext(default_timeout);
    }

    int64_t remain_ms = 0;
    const auto [ptr, ec] = std::from_chars(header_val.data(),
                                           header_val.data() + header_val.size(),
                                           remain_ms);
    if (ec != std::errc() || remain_ms <= 0) {
        return std::nullopt;
    }

    auto effective = std::chrono::milliseconds(remain_ms) - (rtt_estimate / 2);
    if (effective <= std::chrono::milliseconds::zero()) {
        /* Дедлайн вичерпано ще під час транзиту пакета */
        DeadlineContext expired_ctx(std::chrono::milliseconds::zero());
        expired_ctx.cancel();
        return expired_ctx;
    }

    return DeadlineContext(effective);
}
