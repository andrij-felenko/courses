namespace Health {

[[nodiscard]] constexpr uint16_t evaluate_power_rail(uint32_t vdd_mv, uint32_t ripple_mv) noexcept {
    if (vdd_mv < 2800 || vdd_mv > 3600) {
        return 0;
    }

    uint16_t score = 1000;

    if (vdd_mv < 3200) {
        const uint32_t delta_v = 3200 - vdd_mv;
        score -= static_cast<uint16_t>((delta_v * 600) / 400);
    }

    if (ripple_mv > 50) {
        uint32_t excess_ripple = ripple_mv - 50;
        if (excess_ripple > 250) {
            excess_ripple = 250;
        }
        const auto ripple_penalty = static_cast<uint16_t>((excess_ripple * 400) / 250);
        if (score > ripple_penalty) {
            score -= ripple_penalty;
        } else {
            score = 0;
        }
    }

    return score;
}

} // namespace Health
