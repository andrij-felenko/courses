#include "driver/gpio.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define PIN_DO     GPIO_NUM_4      // будь-який вільний GPIO на ESP32
#define WINDOW_MS  300

static const char *TAG = "ky038";
static volatile uint32_t sound_count    = 0;
static volatile uint32_t last_event_isr = 0;
static portMUX_TYPE mux = portMUX_INITIALIZER_UNLOCKED;   // для атомарності на 2 ядрах

static void IRAM_ATTR on_sound(void *arg) {               // ISR у внутрішній RAM
    uint32_t now = (uint32_t)(esp_timer_get_time() / 1000);
    portENTER_CRITICAL_ISR(&mux);
    if (now - last_event_isr > WINDOW_MS) {
        last_event_isr = now;
        sound_count++;
    }
    portEXIT_CRITICAL_ISR(&mux);
}

void app_main(void) {
    gpio_config_t in = {
        .pin_bit_mask = 1ULL << PIN_DO,
        .mode         = GPIO_MODE_INPUT,
        .pull_up_en   = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type    = GPIO_INTR_POSEDGE,     // фронт «тиша → звук»; навпаки — NEGEDGE
    };
    ESP_ERROR_CHECK(gpio_config(&in));
    vTaskDelay(pdMS_TO_TICKS(300));
    ESP_ERROR_CHECK(gpio_install_isr_service(0));          // спільна служба переривань GPIO
    ESP_ERROR_CHECK(gpio_isr_handler_add(PIN_DO, on_sound, NULL));

    uint32_t shown = 0;
    for (;;) {
        portENTER_CRITICAL(&mux);
        uint32_t c = sound_count;
        portEXIT_CRITICAL(&mux);
        if (c != shown) { shown = c; ESP_LOGI(TAG, "подій: %lu", (unsigned long)c); }
        vTaskDelay(pdMS_TO_TICKS(20));
    }
}
