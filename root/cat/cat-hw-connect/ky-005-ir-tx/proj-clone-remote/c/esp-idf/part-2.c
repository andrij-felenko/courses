#include "driver/rmt_tx.h"
#include "freertos/FreeRTOS.h"
#include "ir_nec_encoder.h"        // енкодер NEC з прикладу rmt/ir_nec_transceiver

#define PIN_SEND GPIO_NUM_3        // KY-005 через резистор

void app_main(void) {
    rmt_channel_handle_t tx = NULL;
    rmt_tx_channel_config_t cfg = {
        .clk_src = RMT_CLK_SRC_DEFAULT,
        .resolution_hz = 1000000,   // 1 тик = 1 мкс
        .mem_block_symbols = 64,
        .trans_queue_depth = 4,
        .gpio_num = PIN_SEND,
    };
    ESP_ERROR_CHECK(rmt_new_tx_channel(&cfg, &tx));

    rmt_carrier_config_t carrier = { .frequency_hz = 38000, .duty_cycle = 0.33 };
    ESP_ERROR_CHECK(rmt_apply_carrier(tx, &carrier));   // несучу робить залізо

    rmt_encoder_handle_t nec = NULL;
    ir_nec_encoder_config_t enc = { .resolution = 1000000 };
    ESP_ERROR_CHECK(rmt_new_ir_nec_encoder(&enc, &nec));
    ESP_ERROR_CHECK(rmt_enable(tx));

    rmt_transmit_config_t tcfg = { .loop_count = 0 };
    // зняті адреса й команда — просто вставлені сюди:
    ir_nec_scan_code_t up = { .address = 0xF1, .command = 0x76 };   // «гучність +»
    ir_nec_scan_code_t dn = { .address = 0xF1, .command = 0x77 };   // «гучність −»
    while (1) {
        ESP_ERROR_CHECK(rmt_transmit(tx, nec, &up, sizeof(up), &tcfg));
        vTaskDelay(pdMS_TO_TICKS(2000));
        ESP_ERROR_CHECK(rmt_transmit(tx, nec, &dn, sizeof(dn), &tcfg));
        vTaskDelay(pdMS_TO_TICKS(2000));
    }
}
