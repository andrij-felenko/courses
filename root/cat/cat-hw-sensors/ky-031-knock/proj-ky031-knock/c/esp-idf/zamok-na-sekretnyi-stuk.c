#include <math.h>
#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_timer.h"
#include "esp_log.h"

#define KNOCK       GPIO_NUM_4
#define LED         GPIO_NUM_2       // «замок»: 1 = відчинено
#define LOCKOUT_US   60000
#define GAP_END_US  800000
#define MAXN            12
#define TOL          0.25f           // допуск на частку (безрозмірний)

static const char *TAG = "lock";
static volatile bool knock_flag = false;
static void IRAM_ATTR on_knock(void *arg) { knock_flag = true; }

/* normalize() і rhythm_matches() — та сама чиста арифметика, що у вкладці
   Arduino (нормувати на найдовший проміжок, звірити частки з допуском):
   платформи вона не стосується, тож тут її не повторюємо */
static void normalize(const int64_t *src, int n, float *out);
static bool rhythm_matches(const int64_t *a, int na, const int64_t *b, int nb);

void app_main(void) {
    gpio_config_t in = {
        .pin_bit_mask = 1ULL << KNOCK,
        .mode         = GPIO_MODE_INPUT,
        .pull_up_en   = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type    = GPIO_INTR_NEGEDGE,
    };
    ESP_ERROR_CHECK(gpio_config(&in));
    ESP_ERROR_CHECK(gpio_set_direction(LED, GPIO_MODE_OUTPUT));
    ESP_ERROR_CHECK(gpio_install_isr_service(ESP_INTR_FLAG_IRAM));
    ESP_ERROR_CHECK(gpio_isr_handler_add(KNOCK, on_knock, NULL));
    ESP_LOGI(TAG, "Відстукайте секретний ритм — він стане ключем.");

    int64_t last = 0, gaps[MAXN], secret[MAXN];
    int nGaps = 0, nHits = 0, secretN = 0;
    bool inSeries = false, learning = true;   // перша серія стане еталоном

    while (1) {
        int64_t now = esp_timer_get_time();

        if (knock_flag) {
            knock_flag = false;
            if (now - last > LOCKOUT_US) {
                if (inSeries && nGaps < MAXN) gaps[nGaps++] = now - last;
                last = now; nHits++; inSeries = true;
            }
        }

        if (inSeries && now - last > GAP_END_US) {
            if (learning) {                   // перша серія → запам'ятати як ключ
                for (int i = 0; i < nGaps; i++) secret[i] = gaps[i];
                secretN = nGaps; learning = false;
                ESP_LOGI(TAG, "Ключ записано: %d стук(и). Тепер відстукайте його.", nHits);
            } else if (rhythm_matches(gaps, nGaps, secret, secretN)) {
                ESP_LOGI(TAG, ">>> ВІРНО — відчинено");
                gpio_set_level(LED, 1);
            } else {
                ESP_LOGW(TAG, "... не той ритм");
                gpio_set_level(LED, 0);
            }
            nGaps = 0; nHits = 0; inSeries = false;
        }
        vTaskDelay(pdMS_TO_TICKS(5));
    }
}
