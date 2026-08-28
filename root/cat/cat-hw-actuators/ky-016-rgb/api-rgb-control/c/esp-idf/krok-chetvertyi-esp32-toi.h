// Те саме без обгорток: ledcSetup — це ledc_timer_config(), ledcAttachPin —
// ledc_channel_config(), ledcWrite — ledc_set_duty() + ledc_update_duty().
ledc_timer_config_t timer = {
    .speed_mode      = LEDC_LOW_SPEED_MODE,
    .timer_num       = LEDC_TIMER_0,
    .duty_resolution = LEDC_TIMER_8_BIT,   // 1) роздільність: duty 0..255
    .freq_hz         = 5000,               // 2) частота: 5 кГц
    .clk_cfg         = LEDC_AUTO_CLK,
};
ESP_ERROR_CHECK(ledc_timer_config(&timer));

ledc_channel_config_t ch_r = {            // 3) канал ↔ пін: прив'язка окремим кроком
    .gpio_num = PIN_R, .speed_mode = LEDC_LOW_SPEED_MODE,
    .channel  = LEDC_CHANNEL_0, .timer_sel = LEDC_TIMER_0,
    .duty = 0, .hpoint = 0,
};
ESP_ERROR_CHECK(ledc_channel_config(&ch_r));   // так само CH_G/PIN_G і CH_B/PIN_B

ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, level(gamma8(r)));
ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0);
