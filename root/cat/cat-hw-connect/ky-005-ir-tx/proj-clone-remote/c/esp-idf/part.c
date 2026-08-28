#include "driver/rmt_rx.h"
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "esp_log.h"
#include "ir_nec_encoder.h"   // nec_parse_frame() — з прикладу rmt/ir_nec_transceiver

#define PIN_RECV GPIO_NUM_2   // сюди підключений ІЧ-ПРИЙМАЧ (не передавач!)
static QueueHandle_t q;
static rmt_symbol_word_t symbols[64];

// колбек з ISR: кадр дочитано, віддаємо його задачі
static bool on_done(rmt_channel_handle_t ch, const rmt_rx_done_event_data_t *ed, void *arg) {
    BaseType_t hp = pdFALSE;
    xQueueSendFromISR(q, ed, &hp);
    return hp == pdTRUE;
}

void app_main(void) {
    q = xQueueCreate(4, sizeof(rmt_rx_done_event_data_t));
    rmt_channel_handle_t rx = NULL;
    rmt_rx_channel_config_t cfg = {
        .clk_src = RMT_CLK_SRC_DEFAULT,
        .resolution_hz = 1000000,          // 1 тик = 1 мкс
        .mem_block_symbols = 64,
        .gpio_num = PIN_RECV,
    };
    ESP_ERROR_CHECK(rmt_new_rx_channel(&cfg, &rx));
    rmt_rx_event_callbacks_t cbs = { .on_recv_done = on_done };
    ESP_ERROR_CHECK(rmt_rx_register_event_callbacks(rx, &cbs, NULL));
    ESP_ERROR_CHECK(rmt_enable(rx));

    const rmt_receive_config_t rcfg = {
        .signal_range_min_ns = 1250,       // коротше — то шум
        .signal_range_max_ns = 12000000,   // довше — то вже кінець кадру
    };
    ESP_LOGI("ir", "Тисни кнопки пульта...");
    while (1) {
        ESP_ERROR_CHECK(rmt_receive(rx, symbols, sizeof(symbols), &rcfg));
        rmt_rx_done_event_data_t ed;
        xQueueReceive(q, &ed, portMAX_DELAY);      // прийнято повний кадр
        uint16_t addr, cmd;
        if (nec_parse_frame(ed.received_symbols, ed.num_symbols, &addr, &cmd))
            ESP_LOGI("ir", "NEC address=0x%02X command=0x%02X", addr, cmd);
    }
}
