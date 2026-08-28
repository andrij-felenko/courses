struct ReturnTelemetry {
    std::array<float, 3> pos_current_ned{0.0f, 0.0f, 0.0f}; // Позиція [North, East, Down], м
    std::array<float, 3> pos_home_ned{0.0f, 0.0f, 0.0f};    // Точка Home [North, East, Down], м
    std::array<float, 2> wind_ned{0.0f, 0.0f};            // Вітер [North, East], м/с
    float voltage_v{0.0f};                                // Напруга батареї під навантаженням, В
    float current_a{0.0f};                                // Струм розряду, А
    float energy_remaining_wh{0.0f};                      // Залишкова енергія, Вт·год
    float soc_ratio{1.0f};                                // Ступінь заряду (0.0 … 1.0)
    float r_internal_ohms{0.05f};                         // Внутрішній опір, Ом
    float battery_temp_c{20.0f};                          // Температура блоку, °C
};
