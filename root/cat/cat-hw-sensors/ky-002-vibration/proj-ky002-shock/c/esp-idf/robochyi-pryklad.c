#include "driver/gpio.h"
#include "esp_timer.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define PIN_SHOCK    GPIO_NUM_4      // S давача — будь-яка GPIO з підтяжкою
#define PIN_LED      GPIO_NUM_2      // світлодіод на платі
#define DEBOUNCE_US  60000           // вікно придушення брязкоту, мкс (60 мс)

static const char *TAG = "ky002";

// --- те, що ISR передає задачі; захищено спін-локом ---
static portMUX_TYPE g_mux = portMUX_INITIALIZER_UNLOCKED;
static volatile uint32_t g_edges = 0;        // скільки фронтів прилетіло всього
static volatile int64_t  g_lastEdgeUs = 0;   // час останнього фронту

// ISR: якнайкоротша й обов'язково в IRAM. Жодного ESP_LOG чи обчислень.
static void IRAM_ATTR shock_isr(void *arg) {
    portENTER_CRITICAL_ISR(&g_mux);
    g_edges++;
    g_lastEdgeUs = esp_timer_get_time();     // цей лічильник в ISR читати можна
    portEXIT_CRITICAL_ISR(&g_mux);
}

void app_main(void) {
    gpio_config_t in = {
        .pin_bit_mask = 1ULL << PIN_SHOCK,
        .mode         = GPIO_MODE_INPUT,
        .pull_up_en   = GPIO_PULLUP_ENABLE,       // підтяжка вгору — типовий випадок
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type    = GPIO_INTR_DISABLE,        // фронт виберемо після заміру спокою
    };
    ESP_ERROR_CHECK(gpio_config(&in));
    gpio_config_t out = {
        .pin_bit_mask = 1ULL << PIN_LED,
        .mode         = GPIO_MODE_OUTPUT,
        .pull_up_en   = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type    = GPIO_INTR_DISABLE,
    };
    ESP_ERROR_CHECK(gpio_config(&out));
    vTaskDelay(pdMS_TO_TICKS(50));                // дати входу усталитися

    // --- Автовизначення полярності: що плата тримає у спокої? ---
    int idle = gpio_get_level(PIN_SHOCK);
    ESP_LOGI(TAG, "Рівень спокою = %s",
             idle ? "HIGH (pull-up варіант)" : "LOW (pull-down варіант)");

    // Реагуємо на фронт, що ВІДХОДИТЬ від спокою.
    ESP_ERROR_CHECK(gpio_set_intr_type(PIN_SHOCK,
                    idle ? GPIO_INTR_NEGEDGE : GPIO_INTR_POSEDGE));
    ESP_ERROR_CHECK(gpio_install_isr_service(ESP_INTR_FLAG_IRAM));
    ESP_ERROR_CHECK(gpio_isr_handler_add(PIN_SHOCK, shock_isr, NULL));

    uint32_t seen = 0, shocks = 0;
    int64_t  lastShockUs = 0;
    ESP_LOGI(TAG, "Готовий. Струсіть давач.");

    while (1) {
        uint32_t edges;
        int64_t  lastEdge;
        portENTER_CRITICAL(&g_mux);               // забрати обидва значення цілісно
        edges    = g_edges;
        lastEdge = g_lastEdgeUs;
        portEXIT_CRITICAL(&g_mux);

        if (edges != seen) {                      // прилетіли нові фронти
            seen = edges;
            // Придушення брязкоту без блокування: зараховуємо струс, лише
            // якщо від попереднього зарахованого минуло DEBOUNCE_US.
            if (lastEdge - lastShockUs >= DEBOUNCE_US) {
                lastShockUs = lastEdge;
                ESP_LOGI(TAG, "СТРУС #%u", (unsigned)(++shocks));
                gpio_set_level(PIN_LED, 1);
            }
            // якщо не дотягло до вікна — це відскок пружини, мовчки ігноруємо
        }
        if (esp_timer_get_time() - lastShockUs >= 30000)
            gpio_set_level(PIN_LED, 0);           // погасити через 30 мс

        vTaskDelay(pdMS_TO_TICKS(5));             // віддати такт іншим задачам
    }
}
