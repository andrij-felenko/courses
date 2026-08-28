#include <stdint.h>

// Бітова карта готовності: біт i = 1 → на пріоритеті i є ≥1 готова задача.
// 32 біти ESP32 покривають 32 рівні — достатньо для configMAX_PRIORITIES ≤ 32.
static volatile uint32_t readyBits = 0;

// Встановити біт рівня p (викликати, коли задача рівня p стає готовою).
static inline void setReady(int p) {
    readyBits |= (1u << p);   // бітова маска
}

// Скинути біт рівня p (викликати, коли список рівня p повністю спорожнів).
static inline void clearReady(int p) {
    readyBits &= ~(1u << p);
}

// Повернути номер найвищого готового пріоритету.
// УВАГА: __builtin_clz(0) — невизначена поведінка; захист обов'язковий.
static inline int highestReady(void) {
    if (readyBits == 0) return -1;         // порожня бітмапа — задач немає
    return 31 - __builtin_clz(readyBits);  // GCC → nsau на Xtensa, clz на ARM
}

// --- Числовий приклад ---
// readyBits = 0x0000000A = 0b00000000_00000000_00000000_00001010
//   → біти 1 і 3 зведені (готові пріоритети 1 і 3)
//   → __builtin_clz(0x0000000A) = 28  (28 нулів від MSB до першої одиниці на позиції 3)
//   → highestReady() = 31 − 28 = 3   ✓ найвищий готовий = пріоритет 3
