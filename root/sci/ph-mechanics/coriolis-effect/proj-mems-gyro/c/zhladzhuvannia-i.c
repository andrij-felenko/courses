static float rate_f = 0.0f;   // згладжена кутова швидкість, °/с
static float angle  = 0.0f;   // накопичений кут, °
static uint32_t t_prev = 0;
static float bias_z = 0.0f;

void gyro_init(void) {
    bias_z = gyro_calibrate_zero(512);   // у спокої!
    t_prev = millis();
}

void gyro_update(void) {
    float rate = gyro_rate_dps(bias_z);

    // ФНЧ 1-го порядку: менше alpha — сильніше згладжування, але більша затримка
    const float alpha = 0.15f;
    rate_f += alpha * (rate - rate_f);

    // інтегрування: кут += швидкість × крок часу
    uint32_t now = millis();
    float dt = (now - t_prev) * 1e-3f;   // мс → с
    t_prev = now;
    angle += rate_f * dt;                // ° += (°/с)·с
}
