#include "driver/gpio.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define PIN_SHOCK    GPIO_NUM_4
#define WINDOW_MS    100            // вікно вимірювання сили
#define STRONG_HITS  12             // поріг «сильний струс» (імпульсів за вікно)

static const char *TAG = "ky002";
static portMUX_TYPE g_mux = portMUX_INITIALIZER_UNLOCKED;
static volatile uint32_t g_hits = 0;             // фронти в поточному вікні

static void IRAM_ATTR hit_isr(void *arg) {       // максимально коротка ISR
    portENTER_CRITICAL_ISR(&g_mux);
    g_hits++;
    portEXIT_CRITICAL_ISR(&g_mux);
}

void app_main(void) {
    gpio_config_t in = {
        .pin_bit_mask = 1ULL << PIN_SHOCK,
        .mode         = GPIO_MODE_INPUT,
        .pull_up_en   = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type    = GPIO_INTR_DISABLE,
    };
    ESP_ERROR_CHECK(gpio_config(&in));
    vTaskDelay(pdMS_TO_TICKS(50));

    int idle = gpio_get_level(PIN_SHOCK);
    ESP_ERROR_CHECK(gpio_set_intr_type(PIN_SHOCK,
                    idle ? GPIO_INTR_NEGEDGE : GPIO_INTR_POSEDGE));
    ESP_ERROR_CHECK(gpio_install_isr_service(ESP_INTR_FLAG_IRAM));
    ESP_ERROR_CHECK(gpio_isr_handler_add(PIN_SHOCK, hit_isr, NULL));

    while (1) {
        vTaskDelay(pdMS_TO_TICKS(WINDOW_MS));    // вікно тримає планувальник

        // Забрати й обнулити лічильник вікна атомарно.
        portENTER_CRITICAL(&g_mux);
        uint32_t hits = g_hits;
        g_hits = 0;
        portEXIT_CRITICAL(&g_mux);

        if (hits == 0) continue;                 // тиша — нічого не друкуємо
        ESP_LOGI(TAG, "%s струс: %u імпульсів",
                 hits >= STRONG_HITS ? "СИЛЬНИЙ" : "легкий", (unsigned)hits);
    }
    // інші задачі FreeRTOS увесь час вільні
}
