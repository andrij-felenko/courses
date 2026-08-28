// На ESP32 перехід уміє саме залізо: LEDC має вбудований фейдер, який доводить
// duty до цілі за задані мілісекунди без участі процесора. Кадри рахувати не треба.
#include "driver/ledc.h"

static void fade_ch(ledc_channel_t ch, uint8_t v, uint32_t ms) {
    ledc_set_fade_with_time(LEDC_LOW_SPEED_MODE, ch, level(v), ms);
    ledc_fade_start(LEDC_LOW_SPEED_MODE, ch, LEDC_FADE_NO_WAIT);  // не блокує задачу
}

void fade_to(uint8_t r, uint8_t g, uint8_t b, uint32_t ms) {
    fade_ch(LEDC_CHANNEL_0, r, ms);   // три канали їдуть до цілі одночасно
    fade_ch(LEDC_CHANNEL_1, g, ms);
    fade_ch(LEDC_CHANNEL_2, b, ms);
}

static void rgb_task(void *arg) {
    ESP_ERROR_CHECK(ledc_fade_func_install(0));   // один раз: сервіс фейду + його ISR
    for (;;) {
        fade_to(0, 120, 255, 700);                // помаранчевий → блакитний, 0.7 с
        vTaskDelay(pdMS_TO_TICKS(700));
        fade_to(255, 90, 0, 700);                 // і назад
        vTaskDelay(pdMS_TO_TICKS(700));
    }
}
// у app_main: xTaskCreate(rgb_task, "rgb", 3072, NULL, 5, NULL);
