#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_timer.h"
#include "esp_log.h"

#define HALL_GPIO GPIO_NUM_4
#define POLES     1              // скільки магнітів на оберт
#define STOP_US   2000000        // 2 с без імпульсів → вважаємо, що зупинилось
static const char *TAG = "tacho";

static portMUX_TYPE mux = portMUX_INITIALIZER_UNLOCKED;
static volatile int64_t lastEdge = 0;   // час попереднього фронту, мкс
static volatile int64_t period   = 0;   // останній виміряний період, мкс
static volatile bool    gotPulse = false;

static void IRAM_ATTR on_pulse(void *arg) {
    int64_t now = esp_timer_get_time();  // мкс від старту; в ISR читати можна
    if (lastEdge != 0) {                 // перший фронт лише задає початок відліку
        period   = now - lastEdge;
        gotPulse = true;
    }
    lastEdge = now;
}

void app_main(void) {
    gpio_config_t cfg = {
        .pin_bit_mask = 1ULL << HALL_GPIO,
        .mode         = GPIO_MODE_INPUT,
        .pull_up_en   = GPIO_PULLUP_ENABLE,
        .intr_type    = GPIO_INTR_NEGEDGE,
    };
    gpio_config(&cfg);
    gpio_install_isr_service(0);
    gpio_isr_handler_add(HALL_GPIO, on_pulse, NULL);

    while (1) {
        portENTER_CRITICAL(&mux);
        int64_t T = period, last = lastEdge;
        bool fresh = gotPulse;
        gotPulse = false;
        portEXIT_CRITICAL(&mux);

        if (esp_timer_get_time() - last > STOP_US) {
            ESP_LOGI(TAG, "RPM: 0.0");            // давно немає імпульсів — вал стоїть
        } else if (fresh && T > 0) {
            ESP_LOGI(TAG, "RPM: %.1f", 60000000.0f / ((float)T * POLES));
        }                                         // інакше нового періоду ще нема
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}
