// Те саме на ESP-IDF: шпаруватість приймає драйвер LEDC — окремий блок периферії.
// Записане значення набуває чинності лише після ledc_update_duty().
#include "driver/ledc.h"

void sw_analog(sw_t *s, ledc_channel_t ch, uint8_t duty8) {
    // для active_low інвертуємо: 0 має лишатись «вимкнено»
    uint32_t d = s->active_low ? (uint32_t)(255 - duty8) : duty8;
    ESP_ERROR_CHECK(ledc_set_duty(LEDC_LOW_SPEED_MODE, ch, d));   // 8-бітний таймер → 0…255
    ESP_ERROR_CHECK(ledc_update_duty(LEDC_LOW_SPEED_MODE, ch));
}
