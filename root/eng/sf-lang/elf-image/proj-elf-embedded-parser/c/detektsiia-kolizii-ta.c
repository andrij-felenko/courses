typedef struct {
    uint32_t start;
    uint32_t end;
    uint16_t segment_index;
} MemoryInterval;

bool check_segment_collisions(const Elf32_Phdr* phdr_table, uint16_t phnum) {
    for (uint16_t i = 0; i < phnum; ++i) {
        if (phdr_table[i].p_type != PT_LOAD || phdr_table[i].p_filesz == 0) continue;

        uint32_t start_i = phdr_table[i].p_paddr;
        uint32_t end_i   = start_i + phdr_table[i].p_filesz;

        for (uint16_t j = i + 1; j < phnum; ++j) {
            if (phdr_table[j].p_type != PT_LOAD || phdr_table[j].p_filesz == 0) continue;

            uint32_t start_j = phdr_table[j].p_paddr;
            uint32_t end_j   = start_j + phdr_table[j].p_filesz;

            /* Перевірка умови перетину двох відрізків: max(start_i, start_j) < min(end_i, end_j) */
            uint32_t max_start = (start_i > start_j) ? start_i : start_j;
            uint32_t min_end   = (end_i < end_j) ? end_i : end_j;

            if (max_start < min_end) {
                fprintf(stderr, "КРИТИЧНА ПОМИЛКА: Знайдено накладання пам'яті між сегментами #%u та #%u!\n", i, j);
                fprintf(stderr, "  Діапазон #%u: [0x%08X .. 0x%08X]\n", i, start_i, end_i);
                fprintf(stderr, "  Діапазон #%u: [0x%08X .. 0x%08X]\n", j, start_j, end_j);
                return false; /* Виявлено дефектне лінкування */
            }
        }
    }
    return true; /* Колізій не виявлено */
}
