#include <cstdint>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"

class OV3640PowerController {
public:
    static constexpr gpio_num_t kPinPwdn = GPIO_NUM_21;
    static constexpr gpio_num_t kPinReset = GPIO_NUM_22;

    void powerOnSequence() {
        gpio_config_t io_conf{};
        io_conf.pin_bit_mask = (1ULL << kPinPwdn) | (1ULL << kPinReset);
        io_conf.mode = GPIO_MODE_OUTPUT;
        io_conf.pull_up_en = GPIO_PULLUP_DISABLE;
        io_conf.pull_down_en = GPIO_PULLDOWN_DISABLE;
        io_conf.intr_type = GPIO_INTR_DISABLE;
        gpio_config(&io_conf);

        // Початковий стан: сплячий режим та скидання
        gpio_set_level(kPinPwdn, 1);
        gpio_set_level(kPinReset, 0);
        vTaskDelay(pdMS_TO_TICKS(15));

        // Вихід з PWDN та реліз RESET
        gpio_set_level(kPinPwdn, 0);
        vTaskDelay(pdMS_TO_TICKS(5));
        gpio_set_level(kPinReset, 1);
        vTaskDelay(pdMS_TO_TICKS(20));
    }
};
