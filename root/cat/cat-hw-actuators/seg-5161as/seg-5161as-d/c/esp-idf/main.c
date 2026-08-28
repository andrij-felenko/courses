#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

// Виводи МК під сегменти a,b,c,d,e,f,g,DP (спільний катод: рівень 1 = світиться)
static const gpio_num_t SEG_PIN[8] = {
    GPIO_NUM_2, GPIO_NUM_3, GPIO_NUM_4, GPIO_NUM_5,
    GPIO_NUM_6, GPIO_NUM_7, GPIO_NUM_8, GPIO_NUM_9,   // a b c d e f g DP
};

// Маски цифр 0..9. Біт 0 = a, біт 1 = b, ... біт 6 = g, біт 7 = DP.
static const uint8_t DIGIT[10] = {
    0b00111111, 0b00000110, 0b01011011, 0b01001111, 0b01100110,   // 0 1 2 3 4
    0b01101101, 0b01111101, 0b00000111, 0b01111111, 0b01101111,   // 5 6 7 8 9
};

static void seg_init(void) {
    uint64_t pins = 0;
    for (int i = 0; i < 8; i++) pins |= 1ULL << SEG_PIN[i];
    gpio_config_t cfg = {
        .pin_bit_mask = pins,
        .mode         = GPIO_MODE_OUTPUT,
    };
    ESP_ERROR_CHECK(gpio_config(&cfg));
}

static void seg_show(uint8_t d, bool dot) {
    uint8_t mask = DIGIT[d];
    if (dot) mask |= 0b10000000;                        // засвітити крапку
    for (int i = 0; i < 8; i++)
        gpio_set_level(SEG_PIN[i], (mask >> i) & 1);    // біт -> сегмент
}

void seg_task(void *arg) {
    seg_init();
    for (;;)
        for (uint8_t d = 0; d < 10; d++) {
            seg_show(d, false);
            vTaskDelay(pdMS_TO_TICKS(700));
        }
}
