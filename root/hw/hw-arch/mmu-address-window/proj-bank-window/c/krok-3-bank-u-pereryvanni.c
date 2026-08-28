#include <stdint.h>

// Програмна копія (тінь) регістра: латч часто тільки на запис,
// тож поточний банк тримаємо тут. Оновлюємо РАЗОМ із кожним записом у латч.
static volatile uint8_t current_bank = 0;

// Єдина точка перемикання: пише і в латч, і в тінь — вони не розходяться.
// Відтепер весь код (і обгортки select_bank/read_from_bank) перемикає банк
// лише через set_bank, щоб тінь ніде не відстала від латча.
static inline void set_bank(uint8_t bank) {
    current_bank = bank;           // тінь
    BANK_SEL     = bank;           // латч
}

// Обробник переривання, що теж працює з вікном.
void __interrupt isr_uses_window(void) {
    uint8_t saved = current_bank;  // 1) ЗАПАМ'ЯТАТИ чужий банк на вході

    set_bank(9);                   // 2) увімкнути свій банк і робити діло
    uint8_t sample = WINDOW[0x0000];
    (void)sample;                  // …щось корисне з sample…

    set_bank(saved);               // 3) ВІДНОВИТИ банк, який застали
}
