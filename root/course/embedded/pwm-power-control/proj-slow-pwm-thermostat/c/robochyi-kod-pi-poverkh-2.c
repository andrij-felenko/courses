static pi_t g_pi;

void thermostat_task(void *arg) {
    // Крок петлі — 1 секунда, прив'язаний до мережевого годинника (100 півперіодів).
    pi_init(&g_pi, /*setpoint=*/60.0f, /*kp=*/0.08f, /*ki=*/0.004f, /*dt=*/1.0f);

    uint32_t last_tick = g_halfcycles;
    for (;;) {
        // Чекаємо рівно 100 півперіодів мережі = 1 с (50 Гц) — стабільний крок dt.
        while ((uint32_t)(g_halfcycles - last_tick) < 100) {
            vTaskDelay(pdMS_TO_TICKS(2));
        }
        last_tick += 100;

        float temp = sensor_read_temperature();     // °C, з давача (див. нижче)
        float p = pi_update(&g_pi, temp);           // 0..1
        thermostat_set_power((int32_t)(p * 1000.0f + 0.5f));  // → тисячні у пакетний шар
    }
}
