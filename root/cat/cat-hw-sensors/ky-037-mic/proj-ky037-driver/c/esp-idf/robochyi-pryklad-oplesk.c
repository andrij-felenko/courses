#include "driver/gpio.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <stdbool.h>

#define PIN_SOUND  GPIO_NUM_27         // DO давача
#define PIN_LED    GPIO_NUM_2          // світло / реле, яким керуємо

#define DEAF_MS    250                 // «глухе» вікно після оплеску, мс (гістерезис у часі)

static const char *TAG = "clap";

static int     g_idle;                 // рівень спокою DO (автовизначення)
static bool    g_wasLoud  = false;     // чи було «гучно» на попередньому оберті (для фронту)
static int64_t g_lastClap = 0;         // час останнього ЗАРАХОВАНОГО оплеску
static bool    g_lightOn  = false;     // поточний стан світла

static inline int64_t now_ms(void) { return esp_timer_get_time() / 1000; }
static inline bool isLoud(void) { return gpio_get_level(PIN_SOUND) != g_idle; }

static void clap_task(void *arg) {
    for (;;) {
        bool loud = isLoud();

        // Фронт «тихо → гучно»: цього оберту гучно, а минулого було тихо.
        bool rising = loud && !g_wasLoud;
        g_wasLoud = loud;

        // Зараховуємо оплеск, лише якщо минуло «глухе» вікно від попереднього.
        if (rising && now_ms() - g_lastClap >= DEAF_MS) {
            g_lastClap = now_ms();
            g_lightOn = !g_lightOn;                    // ПЕРЕКИДАЄМО стан
            gpio_set_level(PIN_LED, g_lightOn);
            ESP_LOGI(TAG, "%s", g_lightOn ? "оплеск → УВІМКНЕНО" : "оплеск → вимкнено");
        }
        vTaskDelay(pdMS_TO_TICKS(1));   // віддаємо процесор іншим задачам, фронт не губимо
    }
}

void app_main(void) {
    gpio_config_t in = { .pin_bit_mask = 1ULL << PIN_SOUND, .mode = GPIO_MODE_INPUT,
                         .pull_up_en = GPIO_PULLUP_DISABLE, .pull_down_en = GPIO_PULLDOWN_DISABLE,
                         .intr_type = GPIO_INTR_DISABLE };
    gpio_config_t out = { .pin_bit_mask = 1ULL << PIN_LED, .mode = GPIO_MODE_OUTPUT,
                          .pull_up_en = GPIO_PULLUP_DISABLE, .pull_down_en = GPIO_PULLDOWN_DISABLE,
                          .intr_type = GPIO_INTR_DISABLE };
    ESP_ERROR_CHECK(gpio_config(&in));
    ESP_ERROR_CHECK(gpio_config(&out));

    vTaskDelay(pdMS_TO_TICKS(50));
    g_idle = gpio_get_level(PIN_SOUND);   // тиша = спокій цієї плати
    ESP_LOGI(TAG, "Спокій DO = %s", g_idle ? "HIGH" : "LOW");
    ESP_LOGI(TAG, "Плесни, щоб перемкнути світло.");

    xTaskCreate(clap_task, "clap", 3072, NULL, 5, NULL);
}
