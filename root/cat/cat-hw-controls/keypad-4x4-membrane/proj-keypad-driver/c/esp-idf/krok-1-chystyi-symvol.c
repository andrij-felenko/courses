#include "driver/gpio.h"
#include "esp_rom_sys.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static const char *TAG = "keypad";
#define ROWS 4
#define COLS 4

// що НАДРУКОВАНО на клавіатурі, [рядок][стовпець]:
const char keys[ROWS][COLS] = {
    {'1','2','3','A'},
    {'4','5','6','B'},
    {'7','8','9','C'},
    {'*','0','#','D'}
};
const gpio_num_t row_pins[ROWS] = {GPIO_NUM_32, GPIO_NUM_33, GPIO_NUM_25, GPIO_NUM_26};
const gpio_num_t col_pins[COLS] = {GPIO_NUM_27, GPIO_NUM_14, GPIO_NUM_4,  GPIO_NUM_13};

void keypad_init(void) {
    uint64_t rows_mask = 0, cols_mask = 0;
    for (int r = 0; r < ROWS; r++) rows_mask |= 1ULL << row_pins[r];
    for (int c = 0; c < COLS; c++) cols_mask |= 1ULL << col_pins[c];

    gpio_config_t in = { .pin_bit_mask = rows_mask, .mode = GPIO_MODE_INPUT,
                         .pull_up_en = GPIO_PULLUP_ENABLE,        // рядки у спокої «1»
                         .pull_down_en = GPIO_PULLDOWN_DISABLE,
                         .intr_type = GPIO_INTR_DISABLE };
    gpio_config(&in);
    // стовпці в спокої — у високому опорі («Z»), веденим буде РІВНО один:
    gpio_config_t z = { .pin_bit_mask = cols_mask, .mode = GPIO_MODE_INPUT,
                        .pull_up_en = GPIO_PULLUP_DISABLE,
                        .pull_down_en = GPIO_PULLDOWN_DISABLE,
                        .intr_type = GPIO_INTR_DISABLE };
    gpio_config(&z);
}

// один прохід сітки: 0 — нічого не натиснуто, інакше символ
char keypad_scan(void) {
    for (int c = 0; c < COLS; c++) {
        gpio_set_direction(col_pins[c], GPIO_MODE_OUTPUT);   // цей стовпець веде «0»
        gpio_set_level(col_pins[c], 0);
        esp_rom_delay_us(5);                                 // дати рівню осісти
        char found = 0;
        for (int r = 0; r < ROWS; r++)
            if (gpio_get_level(row_pins[r]) == 0) { found = keys[r][c]; break; }
        gpio_set_direction(col_pins[c], GPIO_MODE_INPUT);    // відпустили у «Z»
        if (found) return found;
    }
    return 0;
}

void app_main(void) {
    keypad_init();
    char prev = 0;
    while (1) {
        char k = keypad_scan();
        if (k && k != prev) ESP_LOGI(TAG, "клавіша: %c", k);  // край, а не рівень
        prev = k;
        vTaskDelay(pdMS_TO_TICKS(20));   // 20 мс — і антидеренч, і поступка іншим задачам
    }
}
