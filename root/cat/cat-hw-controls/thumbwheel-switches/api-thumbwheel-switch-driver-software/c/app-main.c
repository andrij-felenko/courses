// Інтеграція неблокуючого опитування перемикача у головний цикл програми мовою C
#include "thumbwheel.h"

static thumbwheel_t dev;

void app_main(void) {
    thumbwheel_config_t cfg = {
        .data_pins = {GPIO_NUM_4, GPIO_NUM_5, GPIO_NUM_6, GPIO_NUM_7},
        .digit_count = 4,
        .debounce_ms = 50
    };
    
    if (thumbwheel_init(&dev, &cfg) != THUMBWHEEL_OK) {
        return; // Обробка помилки конфігурації
    }

    uint32_t last_value = 0;

    while (1) {
        // Неблокуючий виклик оновлення стану драйвера
        if (thumbwheel_update(&dev) == THUMBWHEEL_OK) {
            uint32_t current_value = thumbwheel_get_value(&dev);
            if (current_value != last_value) {
                last_value = current_value;
                // Використання нової підтвердженої уставки
            }
        }
        
        vTaskDelay(pdMS_TO_TICKS(10)); // Фонова робота системи
    }
}
