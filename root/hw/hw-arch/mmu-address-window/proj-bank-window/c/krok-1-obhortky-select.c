#include <stdint.h>

// Регістр вибору банку — байт у нерухомій частині простору (видно завжди).
#define BANK_SEL   (*(volatile uint8_t *)0x3FF0)

// Вікно: 16 КБ угорі простору, крізь яке видно обраний банк.
#define WINDOW     ((volatile uint8_t *)0xC000)
#define WINDOW_SZ  0x4000u          // 16 КБ = 2¹⁴

// Скільки всього банків (залежить від обсягу зовнішньої пам'яті).
#define BANK_COUNT 32u

// Увімкнути банк у вікні. Після цього виклику крізь WINDOW видно саме його.
static inline void select_bank(uint8_t bank) {
    BANK_SEL = bank;                // один запис у латч — банк перемкнуто
}

// Прочитати байт зі зсуву off усередині банку bank.
uint8_t read_from_bank(uint8_t bank, uint16_t off) {
    select_bank(bank);             // 1) увімкнути потрібний банк…
    return WINDOW[off];            // 2) …і одразу прочитати, поки він активний
}
