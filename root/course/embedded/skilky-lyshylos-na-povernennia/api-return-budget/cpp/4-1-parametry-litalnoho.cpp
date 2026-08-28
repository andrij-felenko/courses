struct ReturnConfig {
    float c_ind{0.0f};                  // Коефіцієнт індуктивного опору (Вт·с/м)
    float c_par{0.0f};                  // Коефіцієнт паразитного опору (Вт·с³/м³)
    float v_air_min_ms{10.0f};          // Мінімальна повітряна швидкість, м/с
    float v_air_max_ms{25.0f};          // Максимальна повітряна швидкість, м/с
    float v_best_range_still_ms{14.0f}; // Швидкість найкращої дальності у штиль, м/с
    float v_climb_ms{3.0f};             // Швидкість набору висоти, м/с
    float p_climb_watts{350.0f};        // Потужність у наборі висоти, Вт
    float v_descend_ms{2.5f};           // Швидкість зниження, м/с
    float p_descend_watts{120.0f};      // Потужність на зниженні, Вт
    float p_hover_watts{450.0f};        // Потужність зависання перед посадкою, Вт
    float p_avionics_watts{25.0f};      // Базове споживання бортової електроніки, Вт
    float t_land_maneuver_sec{45.0f};   // Гарантований час на посадку, с
    float rtl_safe_altitude_m{60.0f};   // Безпечна мінімальна висота повернення, м
    uint8_t cell_count{6};              // Кількість послідовних комірок (6S)
    float cell_v_cutoff{3.0f};          // Критична напруга відсікання на 1 комірку, В
    float nominal_energy_wh{180.0f};    // Паспортна енергоємність збірки, Вт·год
    float reserve_margin_ratio{0.20f};  // Коефіцієнт запасу на пориви вітру (20%)
    float filter_time_constant_s{2.0f}; // Стала часу низькочастотного фільтра, с
};
