struct ReturnBudgetResult {
    float v_air_optimal_ms{0.0f};        // Оптимальна повітряна швидкість V_a*, м/с
    float v_ground_ret_ms{0.0f};         // Шляхова швидкість зближення V_g, м/с
    float wca_rad{0.0f};                 // Кут випередження вітру WCA, рад
    float distance_to_home_m{0.0f};      // Дистанція до точки Home, м
    float time_to_home_sec{0.0f};        // Розрахунковий час повернення, с
    float e_cruise_wh{0.0f};             // Енергія горизонтального перельоту, Вт·год
    float e_climb_wh{0.0f};              // Енергія набору висоти RTL, Вт·год
    float e_land_wh{0.0f};               // Енергія посадки, Вт·год
    float e_reserve_wh{0.0f};            // Запас на пориви, Вт·год
    float e_return_total_wh{0.0f};       // Повна необхідна енергія, Вт·год
    float e_usable_compensated_wh{0.0f}; // Корисна енергія з урахуванням Sag, Вт·год
    float projected_sag_voltage_v{0.0f}; // Прогнозована напруга під тягою, В
    float energy_margin_ratio{0.0f};     // Відносний залишок запасу
    uint8_t state{0};                    // Стан монітора
    bool rtl_mandatory{false};           // true — обов'язковий RTL
};
