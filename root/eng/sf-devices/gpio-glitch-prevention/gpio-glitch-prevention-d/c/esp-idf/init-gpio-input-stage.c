#include "driver/gpio.h"
#include "esp_log.h"

#define INPUT_GPIO_PIN  GPIO_NUM_4

static const char *TAG = "GPIO_SCHMITT";

void init_gpio_input_stage(void)
{
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << INPUT_GPIO_PIN),
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_ANYEDGE
    };
    
    // Налаштування вхідного каскаду: ввімкнення підтяжки та конфігурація піна
    esp_err_t err = gpio_config(&io_conf);
    if (err == ESP_OK) {
        ESP_LOGI(TAG, "Вхідний каскад GPIO %d успішно сконфіговано (з внутрішнім тригером Шмітта)", INPUT_GPIO_PIN);
    }
}

uint32_t read_clean_gpio_level(void)
{
    // Зчитання сформованого цифрового рівня після вхідного тригера Шмітта
    return (uint32_t)gpio_get_level(INPUT_GPIO_PIN);
}
