#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"

#define HALL_GPIO  GPIO_NUM_4    // S давача KY-003 → GPIO4
#define WINDOW_MS  250           // вікно вимірювання
static const char *TAG = "tacho";

static portMUX_TYPE mux = portMUX_INITIALIZER_UNLOCKED;
static volatile uint32_t pulses = 0;   // лічильник, який чіпає ISR

static void IRAM_ATTR on_pulse(void *arg) {   // ISR у RAM: якнайкоротша
    pulses++;
}

void app_main(void) {
    gpio_config_t cfg = {
        .pin_bit_mask = 1ULL << HALL_GPIO,
        .mode         = GPIO_MODE_INPUT,
        .pull_up_en   = GPIO_PULLUP_ENABLE,   // відкритий колектор → підтяжка
        .intr_type    = GPIO_INTR_NEGEDGE,    // спад: магніт зайшов
    };
    gpio_config(&cfg);
    gpio_install_isr_service(0);
    gpio_isr_handler_add(HALL_GPIO, on_pulse, NULL);

    while (1) {
        vTaskDelay(pdMS_TO_TICKS(WINDOW_MS));

        portENTER_CRITICAL(&mux);          // цілісне зчитування й обнулення
        uint32_t n = pulses;
        pulses = 0;
        portEXIT_CRITICAL(&mux);

        float rpm = (float)n * (60000.0f / WINDOW_MS);
        ESP_LOGI(TAG, "RPM: %.0f", rpm);
    }
}
