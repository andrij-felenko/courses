#include "driver/gpio.h"
#include "esp_timer.h"
#include "esp_log.h"

#define BOOT_MARK_GPIO  GPIO_NUM_2   // вільна ніжка під щуп аналізатора

void app_main(void)
{
    // Найперший рядок: підняти ніжку — це «мій код стартував».
    gpio_set_direction(BOOT_MARK_GPIO, GPIO_MODE_OUTPUT);
    gpio_set_level(BOOT_MARK_GPIO, 1);

    // Час від СКИДАННЯ до цієї миті — на аналізаторі (фронт RESET → фронт GPIO).
    // А esp_timer лічить від початку старту ESP-IDF — корисно для відносних замірів.
    int64_t t_since_idf_us = esp_timer_get_time();
    ESP_LOGI("boot", "від старту ESP-IDF до app_main: %lld мкс", t_since_idf_us);

    // ... далі звичайна ініціалізація застосунку ...
}
