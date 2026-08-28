#include "driver/rmt_tx.h"
#include "freertos/FreeRTOS.h"

static rmt_encoder_handle_t enc;                 // «копія» — шле символи як є
static rmt_symbol_word_t frame[34];

static rmt_symbol_word_t sym(uint16_t on, uint16_t off) {   // пачка / тиша, мкс
    return (rmt_symbol_word_t){ .duration0 = on,  .level0 = 1,
                                .duration1 = off, .level1 = 0 };
}

static void nec_send(uint8_t addr, uint8_t cmd) {
    uint32_t w = addr | (uint32_t)(uint8_t)~addr << 8
               | (uint32_t)cmd << 16 | (uint32_t)(uint8_t)~cmd << 24;
    int n = 0;
    frame[n++] = sym(9000, 4500);                     // преамбула
    for (int i = 0; i < 32; i++, w >>= 1)
        frame[n++] = sym(560, (w & 1) ? 1690 : 560);  // «1» — довша пауза
    frame[n++] = sym(560, 0);                         // стоп-імпульс
    rmt_transmit_config_t tc = { .loop_count = 0 };
    ESP_ERROR_CHECK(rmt_transmit(chan, enc, frame, n * sizeof(frame[0]), &tc));
}

void app_main(void) {
    ir_begin(18);
    rmt_copy_encoder_config_t cc = {};
    ESP_ERROR_CHECK(rmt_new_copy_encoder(&cc, &enc));

    while (1) {
        nec_send(0x00, 0x34);                         // адреса 0x00, команда 0x34
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
