#include "driver/rmt_rx.h"       // RMT заміряє тривалості замість бібліотеки
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "esp_log.h"

#define IR_GPIO 4                // вивід S модуля KY-022 → GPIO4
static const char *TAG = "ir";
static QueueHandle_t q;          // готові кадри з переривання в задачу

static bool on_recv_done(rmt_channel_handle_t ch,
                         const rmt_rx_done_event_data_t *ed, void *ctx) {
    BaseType_t hp = pdFALSE;
    xQueueSendFromISR(q, ed, &hp);            // аналог «decode() дав true»
    return hp == pdTRUE;
}

void app_main(void) {
    q = xQueueCreate(1, sizeof(rmt_rx_done_event_data_t));

    rmt_channel_handle_t rx = NULL;
    rmt_rx_channel_config_t ch_cfg = {
        .clk_src = RMT_CLK_SRC_DEFAULT,
        .resolution_hz = 1000000,             // 1 такт = 1 мкс
        .mem_block_symbols = 64,
        .gpio_num = IR_GPIO,
    };
    ESP_ERROR_CHECK(rmt_new_rx_channel(&ch_cfg, &rx));
    rmt_rx_event_callbacks_t cbs = { .on_recv_done = on_recv_done };
    ESP_ERROR_CHECK(rmt_rx_register_event_callbacks(rx, &cbs, NULL));
    ESP_ERROR_CHECK(rmt_enable(rx));          // старт приймача

    rmt_receive_config_t rx_cfg = {
        .signal_range_min_ns = 1250,          // коротше — шум, відкидаємо
        .signal_range_max_ns = 12000000,      // довша пауза = кінець кадру
    };
    static rmt_symbol_word_t raw[64];
    ESP_ERROR_CHECK(rmt_receive(rx, raw, sizeof(raw), &rx_cfg));

    rmt_rx_done_event_data_t frame;
    uint16_t addr, cmd;
    while (1) {
        xQueueReceive(q, &frame, portMAX_DELAY);
        if (nec_decode(frame.received_symbols, frame.num_symbols, &addr, &cmd))
            ESP_LOGI(TAG, "протокол: NEC  адреса: 0x%X  команда: 0x%X", addr, cmd);
        ESP_ERROR_CHECK(rmt_receive(rx, raw, sizeof(raw), &rx_cfg));  // роль resume()
    }
}
