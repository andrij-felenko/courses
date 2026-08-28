namespace driver {

template <typename RegT>
[[nodiscard]] inline Status wait_flag_timeout(
    const volatile RegT* reg,
    RegT flag,
    bool wait_for_set,
    uint32_t timeout_cycles) noexcept {
    while (timeout_cycles > 0) {
        const bool is_set = (*reg & flag) != 0;
        if (is_set == wait_for_set) {
            return Status::Ok;
        }
        --timeout_cycles;
        asm volatile("nop");
    }
    return Status::Timeout;
}

} // namespace driver
