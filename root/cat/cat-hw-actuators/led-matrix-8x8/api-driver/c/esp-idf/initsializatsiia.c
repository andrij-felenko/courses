static const char *TAG = "matrix";

void app_main(void) {
    gpio_config_t io = {
        .pin_bit_mask = 0,
        .mode         = GPIO_MODE_OUTPUT,
        .pull_up_en   = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type    = GPIO_INTR_DISABLE,
    };
    for (int i = 0; i < 8; i++)           // усі шістнадцять ніжок — в одну маску
        io.pin_bit_mask |= (1ULL << COL_PIN[i]) | (1ULL << ROW_PIN[i]);
    ESP_ERROR_CHECK(gpio_config(&io));

    for (int i = 0; i < 8; i++) {
        gpio_set_level(COL_PIN[i], 1);    // стовпець «високий» → цятка темна
        gpio_set_level(ROW_PIN[i], 0);    // ключ закритий → рядок не живиться
    }
    drawSmiley();                         // покладемо в буфер щось видиме
    ESP_LOGI(TAG, "матрицю погашено, запускаю розгортку");
    setupScanTimer();                     // запускаємо розгортку в перериванні
}
