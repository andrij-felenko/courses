/* Оцінити зсув: середнє N відліків, поки апарат ГАРАНТОВАНО нерухомий. */
static float gyro_estimate_bias(int16_t (*read_raw)(void), int n)
{
    float acc = 0.0f;
    for (int i = 0; i < n; i++) {
        acc += gyro_rate_rad(read_raw());    /* уже в рад/с */
        delay_ms(2);                          /* ~500 Гц вибірка */
    }
    return acc / (float)n;                     /* середня «швидкість» спокою = зсув */
}
