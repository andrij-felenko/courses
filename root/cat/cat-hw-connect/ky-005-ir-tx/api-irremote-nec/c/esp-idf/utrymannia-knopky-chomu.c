static const rmt_symbol_word_t nec_repeat[2] = {
    { .duration0 = 9000, .level0 = 1, .duration1 = 2250, .level1 = 0 },
    { .duration0 = 560,  .level0 = 1, .duration1 = 0,    .level1 = 0 },
};

rmt_transmit_config_t tc = { .loop_count = 0 };
nec_send(0x04, 0x34);                             // 1 повний кадр…
for (int i = 0; i < 4; i++) {                     // …і 4 короткі повтори
    vTaskDelay(pdMS_TO_TICKS(40));                // повтор — кожні 110 мс від початку кадру
    ESP_ERROR_CHECK(rmt_transmit(chan, enc, nec_repeat, sizeof(nec_repeat), &tc));
}
