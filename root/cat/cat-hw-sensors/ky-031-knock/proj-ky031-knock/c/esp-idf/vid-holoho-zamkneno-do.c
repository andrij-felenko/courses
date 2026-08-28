#include <stdio.h>
#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_timer.h"
#include "esp_log.h"

#define KNOCK       GPIO_NUM_4
#define LOCKOUT_US   60000     // придушення торохтіння, мкс
#define GAP_END_US  800000     // тиша, що означає «серія скінчилась», мкс
#define MAX_KNOCKS      12     // стелю візерунка обмежуємо

static const char *TAG = "knock";
static volatile bool knock_flag = false;
static void IRAM_ATTR on_knock(void *arg) { knock_flag = true; }

void app_main(void) {
    gpio_config_t in = {
        .pin_bit_mask = 1ULL << KNOCK,
        .mode         = GPIO_MODE_INPUT,
        .pull_up_en   = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type    = GPIO_INTR_NEGEDGE,
    };
    ESP_ERROR_CHECK(gpio_config(&in));
    ESP_ERROR_CHECK(gpio_install_isr_service(ESP_INTR_FLAG_IRAM));
    ESP_ERROR_CHECK(gpio_isr_handler_add(KNOCK, on_knock, NULL));

    int64_t last = 0, gaps[MAX_KNOCKS];   // проміжки між сусідніми стуками
    int n_gaps = 0, n_hits = 0;
    bool in_series = false;

    while (1) {
        int64_t now = esp_timer_get_time();

        // 1) зафіксувати новий стук (з локаутом проти торохтіння)
        if (knock_flag) {
            knock_flag = false;
            if (now - last > LOCKOUT_US) {
                if (in_series && n_gaps < MAX_KNOCKS) gaps[n_gaps++] = now - last;
                last = now;
                n_hits++;
                in_series = true;
            }
        }

        // 2) достатньо довга тиша після стуку → серія скінчилась, розбираємо
        if (in_series && now - last > GAP_END_US) {
            char buf[96] = "";
            int p = 0;
            for (int i = 0; i < n_gaps; i++)
                p += snprintf(buf + p, sizeof(buf) - p, " %lld", gaps[i] / 1000);
            ESP_LOGI(TAG, "серія: %d стук(и), проміжки[мс]:%s", n_hits, buf);
            n_gaps = 0;
            n_hits = 0;
            in_series = false;
        }
        vTaskDelay(pdMS_TO_TICKS(5));
    }
}
