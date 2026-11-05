// Налаштування апаратного цифрового фільтра квадратурного декодера у середовищі ESP-IDF (PCNT / Pulse Counter)
#include "driver/pulse_cnt.h"
#include "esp_log.h"

static const char *TAG = "ENCODER_FILTER";

pcnt_unit_handle_t init_hardware_encoder_with_filter(int gpio_a, int gpio_b) {
    pcnt_unit_config_t unit_config = {
        .low_limit = -32768,
        .high_limit = 32767,
    };
    pcnt_unit_handle_t pcnt_unit = NULL;
    ESP_ERROR_CHECK(pcnt_new_unit(&unit_config, &pcnt_unit));

    // Налаштування вбудованого апаратного цифрового фільтра шуму (Glitch Filter)
    pcnt_glitch_filter_config_t filter_config = {
        .max_glitch_ns = 120, // Усі імпульси коротші за 120 нс відсікаються апаратно
    };
    ESP_ERROR_CHECK(pcnt_unit_set_glitch_filter(pcnt_unit, &filter_config));

    // Створення вхідних каналів для сигналів A та B
    pcnt_chan_config_t chan_a_config = { .edge_gpio_num = gpio_a, .level_gpio_num = gpio_b };
    pcnt_channel_handle_t chan_a = NULL;
    ESP_ERROR_CHECK(pcnt_new_channel(pcnt_unit, &chan_a_config, &chan_a));

    pcnt_chan_config_t chan_b_config = { .edge_gpio_num = gpio_b, .level_gpio_num = gpio_a };
    pcnt_channel_handle_t chan_b = NULL;
    ESP_ERROR_CHECK(pcnt_new_channel(pcnt_unit, &chan_b_config, &chan_b));

    // Налаштування дій по фронтах для квадратурного режиму x4
    ESP_ERROR_CHECK(pcnt_channel_set_edge_action(chan_a, PCNT_CHANNEL_EDGE_ACTION_INCREASE, PCNT_CHANNEL_EDGE_ACTION_DECREASE));
    ESP_ERROR_CHECK(pcnt_channel_set_level_action(chan_a, PCNT_CHANNEL_LEVEL_ACTION_KEEP, PCNT_CHANNEL_LEVEL_ACTION_INVERSE));
    ESP_ERROR_CHECK(pcnt_channel_set_edge_action(chan_b, PCNT_CHANNEL_EDGE_ACTION_INCREASE, PCNT_CHANNEL_EDGE_ACTION_DECREASE));
    ESP_ERROR_CHECK(pcnt_channel_set_level_action(chan_b, PCNT_CHANNEL_LEVEL_ACTION_INVERSE, PCNT_CHANNEL_LEVEL_ACTION_KEEP));

    ESP_ERROR_CHECK(pcnt_unit_enable(pcnt_unit));
    ESP_ERROR_CHECK(pcnt_unit_start(pcnt_unit));
    
    ESP_LOGI(TAG, "Апаратний декодер із цифровим фільтром успішно запущено");
    return pcnt_unit;
}
