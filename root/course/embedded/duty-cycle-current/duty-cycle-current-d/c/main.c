#include <stdint.h>
#include <stdbool.h>

// Чи вигідніший deep-sleep за light-sleep для заданого періоду циклу.
// Усе в цілих: заряд у мкА·с, струми в мкА, період у секундах.
// q_fixed_deep_uA_s — фіксований заряд одного deep-пробудження (boot + конект).
static bool prefer_deep_sleep(uint32_t period_s,
                              uint32_t q_fixed_deep_uA_s,
                              uint32_t i_sleep_light_uA,
                              uint32_t i_sleep_deep_uA) {
    if (i_sleep_light_uA <= i_sleep_deep_uA) return false;  // light не гірший за дном — deep не рятує
    uint32_t d_floor = i_sleep_light_uA - i_sleep_deep_uA;   // наскільки дорожче дно light

    // Порівнюємо БЕЗ ділення, щоб не гнати float і не втрачати точність:
    //   deep вигідний  ⇔  period_s > q_fixed / d_floor
    //   ⇔  period_s * d_floor > q_fixed          (обидва боки × d_floor)
    // period_s * d_floor може перевищити 32 біти → рахуємо у 64.
    uint64_t lhs = (uint64_t)period_s * d_floor;
    return lhs > (uint64_t)q_fixed_deep_uA_s;
}
