/* Правильне знакове розширення (Sign Extension) для 12-бітного Right-Justified числа */
int16_t sign_extend_12bit(uint16_t raw_12) {
    if (raw_12 & 0x0800) {  /* Якщо 11-й біт дорівнює 1 (число від'ємне) */
        raw_12 |= 0xF000;   /* Заповнюємо старші 4 біти одиницями */
    }
    return (int16_t)raw_12;
}

/* Альтернативний швидкий варіант через знаковий арифметичний зсув */
int16_t sign_extend_12bit_shift(uint16_t raw_12) {
    return (int16_t)(raw_12 << 4) >> 4;
}
