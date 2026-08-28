#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"

static const char *TAG = "ky028";
#define DO_PIN  GPIO_NUM_32

static int  rest_level = 1;        // рівень DO у спокої — визначимо на старті
static bool was_hot    = false;    // попередній стан, щоб ловити саме ПЕРЕХІД

// Прочитати «спокій»: кілька замірів, повернути найчастіший рівень.
static int read_rest_level(void) {
    const int N = 15;
    int highs = 0;
    for (int i = 0; i < N; i++) {
        if (gpio_get_level(DO_PIN)) highs++;
        vTaskDelay(pdMS_TO_TICKS(5));
    }
    return (highs > N / 2) ? 1 : 0;            // більшість голосів
}

// «Гаряче» = стан, протилежний до виміряного спокою — полярність-незалежно.
static bool is_hot(void) { return gpio_get_level(DO_PIN) != rest_level; }

void app_main(void) {
    gpio_config_t cfg = {
        .pin_bit_mask = 1ULL << DO_PIN,       .mode         = GPIO_MODE_INPUT,
        .pull_up_en   = GPIO_PULLUP_DISABLE,  .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type    = GPIO_INTR_DISABLE,
    };
    gpio_config(&cfg);

    vTaskDelay(pdMS_TO_TICKS(300));           // дати модулю усталитися після живлення
    rest_level = read_rest_level();           // ВАЖЛИВО: тут температура має бути в НОРМІ
    ESP_LOGI(TAG, "Спокій DO = %s", rest_level ? "HIGH (гаряче буде LOW)"
                                               : "LOW (гаряче буде HIGH)");

    while (1) {
        bool hot = is_hot();
        if (hot != was_hot) {                 // друкуємо лише перехід
            ESP_LOGI(TAG, "%s", hot ? ">> перетнуло поріг: ГАРЯЧЕ"
                                    : "<< нижче порогу: норма");
            was_hot = hot;
        }
        vTaskDelay(pdMS_TO_TICKS(20));
    }
}
