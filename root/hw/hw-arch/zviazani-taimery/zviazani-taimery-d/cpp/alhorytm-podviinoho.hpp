[[nodiscard]] inline std::uint32_t read_cascaded_32bit_atomic(
    volatile const std::uint32_t& master_cnt_reg,
    volatile const std::uint32_t& slave_cnt_reg) noexcept {
    std::uint16_t high1{};
    std::uint16_t low{};
    std::uint16_t high2{};

    do {
        high1 = static_cast<std::uint16_t>(slave_cnt_reg);  // 1. Первинна фіксація старшого слова
        low   = static_cast<std::uint16_t>(master_cnt_reg); // 2. Зчитування молодшого слова
        high2 = static_cast<std::uint16_t>(slave_cnt_reg);  // 3. Повторна перевірка старшого слова
    } while (high1 != high2);

    return (static_cast<std::uint32_t>(high1) << 16) | static_cast<std::uint32_t>(low);
}
