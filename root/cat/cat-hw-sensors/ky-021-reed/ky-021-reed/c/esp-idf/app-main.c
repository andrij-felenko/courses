#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"

#define REED_PIN GPIO_NUM_4

void app_main(void) {
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << REED_PIN),
        .mode = GPIO_MODE_INPUT
    };
    gpio_config(&io_conf);
    
    int last_state = 1;
    while (1) {
        int level = gpio_get_level(REED_PIN);
        if (level == 0 && last_state == 1) {
            // Магніт поруч
        }
        last_state = level;
        vTaskDelay(pdMS_TO_TICKS(50));
    }
}
