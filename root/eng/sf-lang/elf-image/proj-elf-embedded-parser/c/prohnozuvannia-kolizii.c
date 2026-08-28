bool verify_sram_safety_margin(uint32_t data_size, uint32_t bss_size, 
                                uint32_t min_stack_size, uint32_t min_heap_size, 
                                uint32_t sram_capacity_bytes) {
    uint32_t static_usage = data_size + bss_size;
    uint32_t required_minimum = static_usage + min_stack_size + min_heap_size;

    if (required_minimum > sram_capacity_bytes) {
        fprintf(stderr, "КРИТИЧНЕ ПЕРЕПОВНЕННЯ SRAM!\n");
        fprintf(stderr, "  Статичні змінні (.data + .bss): %u B\n", static_usage);
        fprintf(stderr, "  Мінімальний стек + купа:        %u B\n", min_stack_size + min_heap_size);
        fprintf(stderr, "  Фізична ємність SRAM чіпа:      %u B\n", sram_capacity_bytes);
        fprintf(stderr, "  Дефіцит пам'яті:                %u B\n", required_minimum - sram_capacity_bytes);
        return false;
    }

    uint32_t free_margin = sram_capacity_bytes - required_minimum;
    printf("Запас вільної оперативної пам'яті: %u байтів (%.1f%%)\n", 
           free_margin, ((float)free_margin / sram_capacity_bytes) * 100.0f);
    return true;
}
