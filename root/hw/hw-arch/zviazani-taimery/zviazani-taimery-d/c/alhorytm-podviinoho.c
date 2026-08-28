uint32_t timer_cascade_read_32bit_atomic(volatile uint32_t *master_cnt_reg, volatile uint32_t *slave_cnt_reg) {
    uint16_t high1;
    uint16_t low;
    uint16_t high2;

    do {
        high1 = (uint16_t)(*slave_cnt_reg);  // 1. Первинна фіксація старшого слова
        low   = (uint16_t)(*master_cnt_reg); // 2. Зчитування молодшого слова
        high2 = (uint16_t)(*slave_cnt_reg);  // 3. Повторна перевірка старшого слова
    } while (high1 != high2); // Якщо старше слово змінилося під час читання low — повторити

    return ((uint32_t)high1 << 16) | (uint32_t)low;
}
