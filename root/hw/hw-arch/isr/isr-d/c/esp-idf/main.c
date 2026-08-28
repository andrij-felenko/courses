#include "driver/gpio.h"
#include "esp_attr.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define SENSOR GPIO_NUM_4
static const char *TAG = "pulses";
static portMUX_TYPE mux = portMUX_INITIALIZER_UNLOCKED;
static volatile uint32_t pulses = 0;   // спільний лічильник — тому volatile

static void IRAM_ATTR on_pulse(void *arg) {   // короткий обробник, у RAM
    pulses++;                                 // лише рахуємо — і все
}

void app_main(void) {
    gpio_config_t cfg = {
        .pin_bit_mask = 1ULL << SENSOR,
        .mode         = GPIO_MODE_INPUT,
        .pull_up_en   = GPIO_PULLUP_ENABLE,
        .intr_type    = GPIO_INTR_NEGEDGE,    // спад — те саме, що FALLING
    };
    gpio_config(&cfg);
    gpio_install_isr_service(ESP_INTR_FLAG_IRAM);
    gpio_isr_handler_add(SENSOR, on_pulse, NULL);

    while (1) {
        vTaskDelay(pdMS_TO_TICKS(1000));      // раз на секунду
        portENTER_CRITICAL(&mux);             // безпечно зняти спільне значення
        uint32_t n = pulses; pulses = 0;
        portEXIT_CRITICAL(&mux);
        ESP_LOGI(TAG, "%u", (unsigned)n);     // друк — у задачі, НЕ в обробнику
    }
}
