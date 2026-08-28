// ESP-IDF 5.x: те саме без обгортки Arduino
#include <inttypes.h>
#include "driver/gpio.h"
#include "driver/pulse_cnt.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define TACH_GPIO  27
static const char *TAG = "fan";

void app_main(void) {
    gpio_set_pull_mode(TACH_GPIO, GPIO_PULLUP_ONLY);   // сигнал OC — підтяжка обов'язкова

    // 1. Юніт-лічильник із межами (16-бітний: −32768…32767)
    pcnt_unit_config_t unit_cfg = {
        .low_limit  = -1,
        .high_limit = 32767,
    };
    pcnt_unit_handle_t unit = NULL;
    ESP_ERROR_CHECK(pcnt_new_unit(&unit_cfg, &unit));

    // 2. Канал: стежити за фронтами саме на виводі TACH
    pcnt_chan_config_t chan_cfg = {
        .edge_gpio_num  = TACH_GPIO,
        .level_gpio_num = -1,                          // рівень-керування не потрібне
    };
    pcnt_channel_handle_t chan = NULL;
    ESP_ERROR_CHECK(pcnt_new_channel(unit, &chan_cfg, &chan));

    // 3. Висхідний фронт — +1, низхідний — нічого (один імпульс = +1)
    ESP_ERROR_CHECK(pcnt_channel_set_edge_action(chan,
        PCNT_CHANNEL_EDGE_ACTION_INCREASE,
        PCNT_CHANNEL_EDGE_ACTION_HOLD));

    // 4. Фільтр голок: усе коротше за 1 мкс — шум, ігноруємо
    pcnt_glitch_filter_config_t filt = { .max_glitch_ns = 1000 };
    ESP_ERROR_CHECK(pcnt_unit_set_glitch_filter(unit, &filt));

    // 5. Увімкнути → обнулити → запустити
    ESP_ERROR_CHECK(pcnt_unit_enable(unit));
    ESP_ERROR_CHECK(pcnt_unit_clear_count(unit));
    ESP_ERROR_CHECK(pcnt_unit_start(unit));

    while (1) {
        vTaskDelay(pdMS_TO_TICKS(1000));               // вимірюємо рівно за секунду
        int count = 0;
        ESP_ERROR_CHECK(pcnt_unit_get_count(unit, &count));   // залізо вже все порахувало
        ESP_ERROR_CHECK(pcnt_unit_clear_count(unit));         // скид на новий інтервал

        uint32_t rpm = (count / 2) * 60;                      // ÷2 ×60
        ESP_LOGI(TAG, "TACH: %d імп/с  ->  %" PRIu32 " об/хв", count, rpm);
    }
}
