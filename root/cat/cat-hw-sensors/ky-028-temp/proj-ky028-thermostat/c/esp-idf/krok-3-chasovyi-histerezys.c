#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_timer.h"
#include "esp_log.h"

static const char *TAG = "ky028";
#define DO_PIN      GPIO_NUM_32
#define LOAD_PIN    GPIO_NUM_2          // реле/вентилятор (тут — вбудований LED)
#define LOCKOUT_MS  2000                // «карантин» після зміни стану

static int      rest_level = 1;
static bool     state      = false;     // поточний стан термостата: true = «гаряче»
static uint32_t last_flip  = 0;         // коли востаннє перемкнулися, мс

static uint32_t now_ms(void) { return (uint32_t)(esp_timer_get_time() / 1000); }

static int read_rest_level(void) {
    const int N = 15; int highs = 0;
    for (int i = 0; i < N; i++) { if (gpio_get_level(DO_PIN)) highs++;
                                  vTaskDelay(pdMS_TO_TICKS(5)); }
    return (highs > N / 2) ? 1 : 0;
}

static bool raw_hot(void) { return gpio_get_level(DO_PIN) != rest_level; }

void app_main(void) {
    gpio_config_t in = { .pin_bit_mask = 1ULL << DO_PIN, .mode = GPIO_MODE_INPUT,
                         .pull_up_en = GPIO_PULLUP_DISABLE,
                         .pull_down_en = GPIO_PULLDOWN_DISABLE,
                         .intr_type = GPIO_INTR_DISABLE };
    gpio_config(&in);
    gpio_config_t out = { .pin_bit_mask = 1ULL << LOAD_PIN, .mode = GPIO_MODE_OUTPUT };
    gpio_config(&out);

    vTaskDelay(pdMS_TO_TICKS(300));
    rest_level = read_rest_level();
    state = raw_hot();                        // початковий стан — від реальності
    gpio_set_level(LOAD_PIN, state);
    last_flip = now_ms();

    while (1) {
        bool hot = raw_hot();

        // Приймаємо зміну стану, ЛИШЕ якщо минув карантин від минулого перемикання.
        if (hot != state && (now_ms() - last_flip) >= LOCKOUT_MS) {
            state = hot;
            last_flip = now_ms();
            gpio_set_level(LOAD_PIN, state);
            ESP_LOGI(TAG, "%s", state ? ">> увімкнув навантаження (ГАРЯЧЕ)"
                                      : "<< вимкнув навантаження (норма)");
        }

        vTaskDelay(pdMS_TO_TICKS(10));        // задача віддає час іншим, а не спить на зміні
    }
}
