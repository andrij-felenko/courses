#define OVERSAMPLE 16

// Прийняти один кадр 8N1 на голій ніжці. Читання — по центру кожного біта.
// tick() блокує рівно на 1/(16·baud); pin() віддає поточний рівень лінії.
bool soft_uart_rx(uint8_t *out) {
    while (pin() == 1) { /* чекаємо перепад спокій→старт */ }

    // переміститися в СЕРЕДИНУ старт-біта й перевірити, що це не голка шуму
    for (int k = 0; k < OVERSAMPLE / 2; k++) tick();
    if (pin() != 0) return false;           // фальшивий старт — відкинути

    uint8_t data = 0;
    for (int i = 0; i < 8; i++) {
        for (int k = 0; k < OVERSAMPLE; k++) tick();  // крок на цілий біт
        data |= (pin() & 1u) << i;          // зчитуємо по центру, D0 першим
    }

    for (int k = 0; k < OVERSAMPLE; k++) tick();
    if (pin() != 1) return false;           // стоп не «1» → помилка кадру

    *out = data;
    return true;
}
