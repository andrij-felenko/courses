// Буфер 74LVC1G125 живиться від 3.3 В (Vcc = 3V3 МК).
// Його вхід витримує 5 В (5V-tolerant) — тому строб 5 В
// заводимо на буфер напряму, БЕЗ перетворювача рівнів.
// Вихід буфера = чисті 3.3 В → безпечно для піна МК.

#define STROBE_PIN   GPIO_NUM_4        // сюди йде ВИХІД 74LVC (3.3 В)

void strobe_init(void) {
    gpio_config_t io = {
        .pin_bit_mask = 1ULL << STROBE_PIN,
        .mode         = GPIO_MODE_INPUT,
        .pull_up_en   = GPIO_PULLUP_DISABLE,   // буфер сам тримає рівень
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
    };
    gpio_config(&io);
}

// читаємо строб — рівень уже приведений до 3.3 В буфером
static inline int strobe_active(void) {
    return gpio_get_level(STROBE_PIN);         // 1 = строб є
}
