/* ============================================================================
   krok-1-dummy-load-control.c — ESP-IDF: керування баластним навантаженням B0505S
   
   B0505S не має стабілізації. При струмі менше 20 мА (10% від 1 Вт) напруга
   закидається до 6.8–7.2 В. Коли вторинна периферія переходить у режим сну,
   мікроконтролер підключає активний баластний резистор 220 Ом (струм ~23 мА).
   ========================================================================== */

#include <stdio.h>
#include "driver/gpio.h"
#include "esp_log.h"

static const char *TAG = "B0505S_LOAD";

#define GPIO_DUMMY_LOAD_EN   GPIO_NUM_22  // Керування баластом (HIGH = підключити 220 Ом)
#define GPIO_ISO_PWR_EN      GPIO_NUM_23  // Первинне живлення B0505S (HIGH = ON)

void b0505s_init(void) {
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << GPIO_DUMMY_LOAD_EN) | (1ULL << GPIO_ISO_PWR_EN),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_ENABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    gpio_config(&io_conf);

    // 1. Вмикаємо баласт ще до старту перетворювача, щоб уникнути стрибка на холостому ходу
    gpio_set_level(GPIO_DUMMY_LOAD_EN, 1);
    
    // 2. Подаємо вхідні +5 В на B0505S
    gpio_set_level(GPIO_ISO_PWR_EN, 1);
    ESP_LOGI(TAG, "B0505S запущено з активним баластом 220 Ом");
}

void b0505s_set_peripheral_active(bool active) {
    if (active) {
        // Коли ізольований трансивер прокинувся і сам споживає > 30 мА,
        // баластний резистор вимикається для економії енергії
        gpio_set_level(GPIO_DUMMY_LOAD_EN, 0);
        ESP_LOGI(TAG, "Периферія активна: баласт вимкнено");
    } else {
        // Перед переведенням периферії у сон підключаємо баласт назад
        gpio_set_level(GPIO_DUMMY_LOAD_EN, 1);
        ESP_LOGI(TAG, "Периферія у сні: баласт підключено (захист від закидання напруги)");
    }
}
