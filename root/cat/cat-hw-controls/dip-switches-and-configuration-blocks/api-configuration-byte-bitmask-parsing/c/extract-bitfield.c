// Виділення бітового поля заданої ширини та зсуву
uint8_t extract_bitfield(uint8_t byte_val, uint8_t offset, uint8_t width) {
    uint8_t mask = (uint8_t)((1U << width) - 1U);
    return (uint8_t)((byte_val >> offset) & mask);
}

// Зчитування з програмним дебаунсингом (потрібно 3 однакові зчитування)
uint8_t read_debounced_config(void) {
    uint8_t last_val = shift_register_read_byte();
    uint8_t match_count = 0;

    while (match_count < 2) {
        delay_ms(5);
        uint8_t current_val = shift_register_read_byte();
        if (current_val == last_val) {
            match_count++;
        } else {
            last_val = current_val;
            match_count = 0;
        }
    }
    return last_val;
}
