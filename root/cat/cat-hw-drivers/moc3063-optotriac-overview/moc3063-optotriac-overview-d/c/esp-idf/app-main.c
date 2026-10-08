#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

// Призначення піна керування оптосимістором MOC3063
#define MOC3063_GPIO_PIN GPIO_NUM_18

void app_main(void) {
    // Налаштування конфігурації виводу GPIO
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << MOC3063_GPIO_PIN),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE
    };
    gpio_config(&io_conf);

    // Увімкнення навантаження (подача низького рівня вмикає світлодіод за схемою Sinking)
    gpio_set_level(MOC3063_GPIO_PIN, 0);
    vTaskDelay(pdMS_TO_TICKS(5000)); // Навантаження працює 5 секунд

    // Вимкнення навантаження (високий рівень припиняє проходження струму через світлодіод)
    gpio_set_level(MOC3063_GPIO_PIN, 1);
}
