// Приклад: фільтруємо вісь гіроскопа в циклі вибірки 1 кГц.
static kalman_robust_t g_gyro;

void gyro_filter_setup(void)
{
    // x0=0; Qx, Qb, R — з розділу про налаштування нижче; ворота 3σ.
    kr_init(&g_gyro, 0.0f,
            /*Qx*/ 1.0e-4f, /*Qb*/ 1.0e-6f, /*R*/ 4.0e-2f, /*gate*/ 3.0f);
    // Температурна модель зі сторінки даташита (нахил нуля по температурі):
    kr_set_temp_model(&g_gyro, /*T0*/ 25.0f, /*kT*/ 0.01f);  // °/с на °C
}

// Викликається з переривання таймера на 1 кГц (Δt = 1 мс).
void on_adc_sample(void)
{
    float raw  = gyro_read_dps();        // сирий вимір, °/с
    float temp = gyro_read_temp_c();     // температура кристала, °C

    float rate = kr_step(&g_gyro, raw, temp);   // очищена кутова швидкість

    // Діагностика розходження: нев'язка має скакати навколо нуля.
    // Стало однобока → Q/R погані. Тут — найпростіший ковзний слід.
    static float innov_avg = 0.0f;
    innov_avg += 0.001f * (g_gyro.last_innov - innov_avg);  // повільне середнє
    if (fabsf(innov_avg) > DIVERGENCE_LIMIT) {
        flag_filter_health_bad();        // у лог / на світлодіод / у телеметрію
    }

    use_angular_rate(rate);              // далі — інтегрування в кут, керування
}
