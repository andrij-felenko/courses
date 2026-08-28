// 74HC595: виставляємо один байт на 8 виходів, зсуваючи біти вручну.
// DS(14)→GPIO23, SHCP(11)→GPIO18, STCP(12)→GPIO5.
// OE(13)→GND, MR(10)→+3V3, Vcc(16)→+3V3, GND(8)→спільна.
#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define DATA   GPIO_NUM_23   // → DS
#define CLOCK  GPIO_NUM_18   // → SHCP
#define LATCH  GPIO_NUM_5    // → STCP

static void shift_out(uint8_t value) {           // зі старшого біта
    for (int i = 7; i >= 0; i--) {
        gpio_set_level(DATA, (value >> i) & 1);  // виставили біт
        gpio_set_level(CLOCK, 1);                // клацнули такт — чип узяв його
        gpio_set_level(CLOCK, 0);
    }
}

static void write_byte(uint8_t value) {
    gpio_set_level(LATCH, 0);                    // закриваємо засувку: набираємось потай
    shift_out(value);                            // 8 тактів: заштовхали 8 бітів
    gpio_set_level(LATCH, 1);                    // фронт засувки → усі 8 виходів оновились разом
}

void app_main(void) {
    gpio_config_t io = {
        .pin_bit_mask = (1ULL << DATA) | (1ULL << CLOCK) | (1ULL << LATCH),
        .mode = GPIO_MODE_OUTPUT,
    };
    gpio_config(&io);

    while (1) {
        // «біжуча одиниця»: по черзі запалюємо кожен вихід
        for (int i = 0; i < 8; i++) {
            write_byte(1 << i);
            vTaskDelay(pdMS_TO_TICKS(120));
        }
    }
}
