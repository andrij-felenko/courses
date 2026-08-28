#include "driver/gpio.h"

#define ROWS 4
#define COLS 4
static const int row_pin[ROWS] = { 12, 13, 14, 27 };
static const int col_pin[COLS] = { 16, 17, 18, 19 };

void matrix_init(void) {
    for (int c = 0; c < COLS; c++) {
        gpio_set_direction(col_pin[c], GPIO_MODE_INPUT);
        gpio_set_pull_mode(col_pin[c], GPIO_PULLUP_ONLY);  /* спокій = HIGH */
    }
    for (int r = 0; r < ROWS; r++)                          /* рядки поки «відпущені» */
        gpio_set_direction(row_pin[r], GPIO_MODE_INPUT);
}

/* повертає 16 бітів: біт (r*COLS + c) = 1, якщо клавішу натиснуто */
uint16_t matrix_scan(void) {
    uint16_t keys = 0;
    for (int r = 0; r < ROWS; r++) {
        gpio_set_direction(row_pin[r], GPIO_MODE_OUTPUT);   /* активуємо рядок */
        gpio_set_level(row_pin[r], 0);                      /* притягуємо до нуля */
        esp_rom_delay_us(5);                                /* дати лінії осісти */

        for (int c = 0; c < COLS; c++)
            if (gpio_get_level(col_pin[c]) == 0)            /* стовпець упав → натиск */
                keys |= (uint16_t)(1u << (r * COLS + c));

        gpio_set_direction(row_pin[r], GPIO_MODE_INPUT);    /* «відпускаємо» рядок */
    }
    return keys;
}
