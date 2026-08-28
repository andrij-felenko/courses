// Ручне керування FEM двома ніжками. Безпечне перемикання режимів:
// НІКОЛИ не тримати TX_EN і RX_EN активними водночас (стан 11 палить LNA).
#define FEM_TX_EN  25   // ніжка "увімкнути передачу"
#define FEM_RX_EN  26   // ніжка "увімкнути прийом"

static void fem_sleep(void) {           // 00 — сон, усе вимкнено
    gpio_clear(FEM_TX_EN);
    gpio_clear(FEM_RX_EN);
}

static void fem_rx(void) {              // 01 — прийом
    gpio_clear(FEM_TX_EN);              // СПЕРШУ гасимо передачу
    gpio_set(FEM_RX_EN);               // і лише тоді вмикаємо прийом
}

static void fem_tx(void) {             // 10 — передача
    gpio_clear(FEM_RX_EN);             // СПЕРШУ гасимо прийом (бережемо LNA)
    gpio_set(FEM_TX_EN);               // тоді пускаємо PA
}
