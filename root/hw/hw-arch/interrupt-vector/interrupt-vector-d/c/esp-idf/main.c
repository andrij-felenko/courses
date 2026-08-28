#include "driver/gpio.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static const char *TAG = "button";
static volatile bool pressed = false;   // ISR і задача бачать ту саму змінну

static void IRAM_ATTR on_button(void *arg) {   // IRAM_ATTR: обробник тримати в RAM
    pressed = true;                            // одна дешева дія — і все
}

void app_main(void) {
    gpio_config_t cfg = {
        .pin_bit_mask = 1ULL << GPIO_NUM_0,
        .mode         = GPIO_MODE_INPUT,
        .pull_up_en   = GPIO_PULLUP_ENABLE,    // підтяжка догори
        .intr_type    = GPIO_INTR_NEGEDGE,     // спад: кнопка тягне вхід до землі
    };
    gpio_config(&cfg);
    gpio_install_isr_service(0);               // той самий спільний обробник GPIO
    gpio_isr_handler_add(GPIO_NUM_0, on_button, NULL);

    while (1) {                                // важку роботу робимо ТУТ, поза ISR
        if (pressed) {
            pressed = false;
            ESP_LOGI(TAG, "кнопку натиснуто");
        }
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}
