// (а) правильно: порівняння, не присвоєння
if (gpio_get_level(GPIO_NUM_2) != 0) {
    ESP_LOGI(TAG, "triggered");
}

// (б) правильно: тип тримає всю ширину маски
uint64_t mask = (1ULL << 9);           // pin_bit_mask — 64-розрядне поле
gpio_config_t io = {
    .pin_bit_mask = mask,
    .mode = GPIO_MODE_OUTPUT,
};
ESP_ERROR_CHECK(gpio_config(&io));

// або якщо потрібен саме uint8_t — біт має влазити (0..7, не 9):
uint8_t mask8 = (1U << 2);             // 0x04 — влазить у uint8_t
