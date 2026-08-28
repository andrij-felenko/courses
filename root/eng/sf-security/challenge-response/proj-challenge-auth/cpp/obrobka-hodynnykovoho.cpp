constexpr std::chrono::seconds MaxClockSkew{5};

[[nodiscard]] bool is_timestamp_valid(std::chrono::seconds token_time,
                                      std::chrono::seconds now_time,
                                      std::chrono::seconds max_age) noexcept {
    if (token_time > now_time) {
        return (token_time - now_time) <= MaxClockSkew;
    }
    return (now_time - token_time) <= max_age;
}
