#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

// три вільні виводи, підведені до ліній шилда LATCH/CLK/DATA
#define LATCH  GPIO_NUM_18   // ST_CP — «клац», виставити біти
#define CLK    GPIO_NUM_19   // SH_CP — тактує зсув
#define DATA   GPIO_NUM_21   // DS    — біти по одному

// байти сегментів для цифр 0..9 (спільний анод: 0 = світиться)
static const uint8_t SEG[10] = {
    0xC0, 0xF9, 0xA4, 0xB0, 0x99, 0x92, 0x82, 0xF8, 0x80, 0x90
};
static const uint8_t SEL[4] = { 0xF1, 0xF2, 0xF4, 0xF8 };

static void display_init(void) {
    gpio_config_t cfg = {
        .pin_bit_mask = (1ULL << LATCH) | (1ULL << CLK) | (1ULL << DATA),
        .mode         = GPIO_MODE_OUTPUT,
    };
    gpio_config(&cfg);
}

static void shift_out(uint8_t b) {          // старший біт першим
    for (int i = 7; i >= 0; i--) {
        gpio_set_level(DATA, (b >> i) & 1);
        gpio_set_level(CLK, 1);             // фронт такту заштовхує біт
        gpio_set_level(CLK, 0);
    }
}

static void show_digit(uint8_t value, uint8_t pos) {
    gpio_set_level(LATCH, 0);   // латч униз — набираємо
    shift_out(SEG[value]);      // спершу байт сегментів
    shift_out(SEL[pos]);        // потім байт вибору розряду
    gpio_set_level(LATCH, 1);   // клац — виставити на виходи
}

void app_main(void) {
    display_init();
    while (1) {
        show_digit(5, 0);       // цифра «5» у першому (правому) розряді
        vTaskDelay(pdMS_TO_TICKS(5));
    }
}
