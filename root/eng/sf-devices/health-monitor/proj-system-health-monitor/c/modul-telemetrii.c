uint16_t health_evaluate_power_rail(uint32_t vdd_mv, uint32_t ripple_mv) {
    if (vdd_mv < 2800 || vdd_mv > 3600) {
        return 0; // Неприпустима напруга
    }

    uint16_t score = 1000;

    // Штраф за просідання напруги нижче 3200 мВ
    if (vdd_mv < 3200) {
        uint32_t delta_v = 3200 - vdd_mv; // 0..400 мВ
        score -= (uint16_t)((delta_v * 600) / 400);
    }

    // Штраф за пульсації понад 50 мВ
    if (ripple_mv > 50) {
        uint32_t excess_ripple = ripple_mv - 50;
        if (excess_ripple > 250) {
            excess_ripple = 250;
        }
        uint16_t ripple_penalty = (uint16_t)((excess_ripple * 400) / 250);
        if (score > ripple_penalty) {
            score -= ripple_penalty;
        } else {
            score = 0;
        }
    }

    return score;
}
