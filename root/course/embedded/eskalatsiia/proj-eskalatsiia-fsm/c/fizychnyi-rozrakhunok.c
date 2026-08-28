/* Розрахунок дедлайну в мілісекундах */
uint32_t calculate_dynamic_deadline_ms(float distance_to_obstacle_m,
                                       float current_speed_mps,
                                       float max_braking_decel_mps2,
                                       float safety_margin_m,
                                       uint32_t sensor_lag_ms)
{
    /* Якщо апарат стоїть або швидкість мізерна — таймаут обмежується зависанням */
    if (current_speed_mps < 0.1f) {
        return 15000; /* 15 секунд на місці */
    }

    /* Гальмівний шлях: S_brake = V^2 / (2 * a) */
    float braking_distance_m = (current_speed_mps * current_speed_mps) / (2.0f * max_braking_decel_mps2);
    float total_safe_distance_m = braking_distance_m + safety_margin_m;

    /* Якщо вже ближче за гальмівний шлях із запасом — нульовий час, гальмувати негайно */
    if (distance_to_obstacle_m <= total_safe_distance_m) {
        return 0;
    }

    /* Доступна дистанція вільного руху до точки початку екстреного гальмування */
    float distance_available_m = distance_to_obstacle_m - total_safe_distance_m;
    float time_available_sec = distance_available_m / current_speed_mps;

    uint32_t time_available_ms = (uint32_t)(time_available_sec * 1000.0f);
    if (time_available_ms <= sensor_lag_ms) {
        return 0;
    }

    return time_available_ms - sensor_lag_ms;
}
