typedef struct {
    uint32_t current_address;
    uint32_t start_address;
    uint32_t end_address;
    uint32_t single_bit_errors;
    uint32_t double_bit_errors;
} health_flash_scrubber_t;

void health_flash_scrubber_init(health_flash_scrubber_t *scrubber, uint32_t start, uint32_t end) {
    if (!scrubber) return;
    scrubber->start_address = start;
    scrubber->end_address = end;
    scrubber->current_address = start;
    scrubber->single_bit_errors = 0;
    scrubber->double_bit_errors = 0;
}

void health_flash_scrubber_step(health_flash_scrubber_t *scrubber, size_t words_to_read) {
    if (!scrubber || scrubber->start_address >= scrubber->end_address) return;

    volatile const uint32_t *ptr = (volatile const uint32_t *)scrubber->current_address;
    for (size_t i = 0; i < words_to_read; ++i) {
        // Фіктивне читання для провокації апаратного блоку ECC
        volatile uint32_t dummy = *ptr++;
        (void)dummy;

        scrubber->current_address += sizeof(uint32_t);
        if (scrubber->current_address >= scrubber->end_address) {
            scrubber->current_address = scrubber->start_address; // Зациклення
            break;
        }
    }
}
