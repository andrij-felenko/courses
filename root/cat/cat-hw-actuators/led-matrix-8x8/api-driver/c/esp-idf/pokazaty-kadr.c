void app_main(void) {
    gpio_config_t io = {
        .pin_bit_mask = (1ULL << PIN_DIN) | (1ULL << PIN_CLK) | (1ULL << PIN_LOAD),
        .mode         = GPIO_MODE_OUTPUT,
        .pull_up_en   = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type    = GPIO_INTR_DISABLE,
    };
    ESP_ERROR_CHECK(gpio_config(&io));
    max7219init();
    drawSmiley();
    max7219show();     // надіслали кадр — і він стоїть сам, чип його розгортає

    // Нічого крутити не треба: MAX7219 сам тримає й розгортає картинку.
    // Щоб змінити зображення — перепиши frame[] і виклич max7219show() ще раз.
    for (;;) vTaskDelay(pdMS_TO_TICKS(1000));
}
