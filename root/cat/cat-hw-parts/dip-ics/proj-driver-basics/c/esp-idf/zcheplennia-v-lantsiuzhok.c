// 74HC595 → ULN2003: регістр адресує канали, масив тягне їхній струм.
// Q0..Q6 регістра → IN1..IN7 масиву. COM(9) масиву → +V навантаження.
// Кожен «1» у байті → відповідний вихід ULN2003 стягує своє навантаження в −.
static void set_channels(uint8_t mask) {   // біт i маски → канал (i+1) масиву
    gpio_set_level(LATCH, 0);
    shift_out(mask);
    gpio_set_level(LATCH, 1);
}

void app_main(void) {
    gpio_config_t io = {
        .pin_bit_mask = (1ULL << DATA) | (1ULL << CLOCK) | (1ULL << LATCH),
        .mode = GPIO_MODE_OUTPUT,
    };
    gpio_config(&io);

    while (1) {
        set_channels(0b00000011);  vTaskDelay(pdMS_TO_TICKS(1000));  // канали 1 і 2 (напр. два реле)
        set_channels(0b01001000);  vTaskDelay(pdMS_TO_TICKS(1000));  // канали 4 і 7
        set_channels(0b00000000);  vTaskDelay(pdMS_TO_TICKS(1000));  // усе вимкнули
    }
}
