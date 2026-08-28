#include "driver/rmt_rx.h"        // RMT міряє довжини імпульсів апаратно
#include "freertos/queue.h"
#include "esp_log.h"

#define IR_GPIO GPIO_NUM_4        // вивід S модуля KY-022
static const char *TAG = "ir";

static QueueHandle_t q;
static rmt_symbol_word_t raw[64];

// колбек: кадр домовчав — віддаємо зібрані символи в чергу
static bool on_done(rmt_channel_handle_t ch,
                    const rmt_rx_done_event_data_t *ev, void *ctx)
{
    BaseType_t woken = pdFALSE;
    xQueueSendFromISR(q, ev, &woken);
    return woken == pdTRUE;
}

void ir_task(void *arg)
{
    q = xQueueCreate(4, sizeof(rmt_rx_done_event_data_t));

    rmt_channel_handle_t rx = NULL;
    rmt_rx_channel_config_t cfg = {
        .gpio_num          = IR_GPIO,
        .clk_src           = RMT_CLK_SRC_DEFAULT,
        .resolution_hz     = 1000000,   // 1 МГц → крок вимірювання 1 мкс
        .mem_block_symbols = 64,
    };
    ESP_ERROR_CHECK(rmt_new_rx_channel(&cfg, &rx));

    rmt_rx_event_callbacks_t cbs = { .on_recv_done = on_done };
    ESP_ERROR_CHECK(rmt_rx_register_event_callbacks(rx, &cbs, NULL));
    ESP_ERROR_CHECK(rmt_enable(rx));

    // коротше за 1.25 мкс — шум; пауза довша за 12 мс — кінець кадру
    rmt_receive_config_t rc = { .signal_range_min_ns = 1250,
                                .signal_range_max_ns = 12000000 };
    ESP_ERROR_CHECK(rmt_receive(rx, raw, sizeof(raw), &rc));

    rmt_rx_done_event_data_t ev;
    uint16_t addr, cmd;
    while (1) {
        xQueueReceive(q, &ev, portMAX_DELAY);
        // nec_decode() — власний розбір довжин: готового декодера в ESP-IDF нема
        if (nec_decode(ev.received_symbols, ev.num_symbols, &addr, &cmd))
            ESP_LOGI(TAG, "протокол: NEC  команда: 0x%02X", cmd);
        ESP_ERROR_CHECK(rmt_receive(rx, raw, sizeof(raw), &rc));  // під наступний кадр
    }
}
