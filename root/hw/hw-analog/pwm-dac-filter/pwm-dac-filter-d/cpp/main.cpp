#include <cstdint>

constexpr uint8_t  PWM_TOP = 255u;     // лічильник 0..255 -> 8 розрядів, 256 рівнів
constexpr uint16_t VDD_MV  = 3300u;    // живлення в мілівольтах

// Задати поріг порівняння = ширину імпульсу (0..PWM_TOP).
// Залізо саме формує ШІМ; процесор лише оновлює це число.
static inline void pwm_set_level(uint8_t level) {
    OCR_REG = level;        // OCR_REG — регістр порівняння таймера
}

// Перевести бажану напругу (мВ) на код шпаруватості й виставити її.
void dac_set_mv(uint16_t want_mv) {
    if (want_mv > VDD_MV) want_mv = VDD_MV;          // не вище живлення
    // level = want_mv / VDD * TOP, рахуємо в цілих без втрати точності:
    uint16_t level = ((uint32_t)want_mv * PWM_TOP + VDD_MV / 2) / VDD_MV;
    pwm_set_level((uint8_t)level);                   // +VDD/2 — округлення до найближчого
}
