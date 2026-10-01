#include "driver/gpio.h"
#include "esp_timer.h"

#define HALL_PIN GPIO_NUM_4

static volatile uint32_t pulse_count = 0;
static volatile int64_t last_time = 0;

static void IRAM_ATTR gpio_isr_handler(void* arg) {
    int64_t now = esp_timer_get_time();
    if (now - last_time > 1000) {
        pulse_count++;
        last_time = now;
    }
}

void app_main(void) {
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << HALL_PIN),
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .intr_type = GPIO_INTR_NEGEDGE
    };
    gpio_config(&io_conf);
    gpio_install_isr_service(0);
    gpio_isr_handler_add(HALL_PIN, gpio_isr_handler, NULL);
}
