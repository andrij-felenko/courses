// Група каналів (напр. R, G, B одного пікселя або кілька зон підсвітки).
#define DIM_GROUP_N   3
static const dim_ch_t g_group[DIM_GROUP_N] = {
    { .gpio = 25, .channel = LEDC_CHANNEL_0 },   // R
    { .gpio = 26, .channel = LEDC_CHANNEL_1 },   // G
    { .gpio = 27, .channel = LEDC_CHANNEL_2 },   // B
};

// Миттєво й СИНХРОННО виставити рівні всіх каналів групи (без fade).
// Спершу заряджаємо duty у тіньові регістри БЕЗ застосування,
// потім одним викликом даємо їм набути чинності від спільного фронту.
static void dim_group_set_sync(const uint8_t level[DIM_GROUP_N]) {
    for (int i = 0; i < DIM_GROUP_N; i++) {
        uint16_t duty = g_gamma_lut[level[i]];
        // set_duty записує в буфер; update_duty застосовує. Тут — тільки set:
        ESP_ERROR_CHECK(ledc_set_duty(DIM_MODE, g_group[i].channel, duty));
    }
    // Тепер застосовуємо всі разом — фронти збігаються.
    for (int i = 0; i < DIM_GROUP_N; i++) {
        ESP_ERROR_CHECK(ledc_update_duty(DIM_MODE, g_group[i].channel));
    }
}
