#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

// Вісім входів масиву (IN1..IN8) на восьми виводах контролера.
// Масив — стік: логічна 1 на INk відкриває канал і притягує OUTk до землі.
static const gpio_num_t IN_PIN[8] = {
    GPIO_NUM_4,  GPIO_NUM_5,  GPIO_NUM_16, GPIO_NUM_17,
    GPIO_NUM_18, GPIO_NUM_19, GPIO_NUM_21, GPIO_NUM_22,
};

static void relays_init(void) {
    uint64_t mask = 0;
    for (int ch = 0; ch < 8; ch++) mask |= 1ULL << IN_PIN[ch];

    gpio_config_t cfg = {
        .pin_bit_mask = mask,
        .mode         = GPIO_MODE_OUTPUT,
        .pull_up_en   = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type    = GPIO_INTR_DISABLE,
    };
    ESP_ERROR_CHECK(gpio_config(&cfg));

    for (int ch = 0; ch < 8; ch++)
        gpio_set_level(IN_PIN[ch], 0);      // старт: усі канали закриті, реле відпущені
}

static void relay_set(int ch, int on) { gpio_set_level(IN_PIN[ch], on ? 1 : 0); }

// Виставити одразу весь банк за бітовою маскою: біт k = 1 → реле k увімкнено.
static void relay_bank(uint8_t mask) {
    for (int ch = 0; ch < 8; ch++)
        gpio_set_level(IN_PIN[ch], (mask >> ch) & 1);
}

void app_main(void) {
    relays_init();
    for (;;) {
        relay_set(0, 1);                    // клацнули перше реле
        vTaskDelay(pdMS_TO_TICKS(500));
        relay_set(0, 0);
        vTaskDelay(pdMS_TO_TICKS(500));
        relay_bank(0b10101010);             // увімкнули реле 1, 3, 5, 7 воднораз
        vTaskDelay(pdMS_TO_TICKS(500));
        relay_bank(0x00);                   // усі відпустили
        vTaskDelay(pdMS_TO_TICKS(500));
    }
}
