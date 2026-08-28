#include <cstdint>
#include <algorithm>

constexpr int32_t PWM_TOP     =   500;          // рівні шпаруватості 0..500 (~9 біт)
constexpr int32_t IN_MAX      = 65535;          // повний розмах 16-бітного входу
constexpr int32_t STATE_CLAMP = 4 * IN_MAX;     // страхувальна межа для станів похибки

// Простий і швидкий генератор псевдовипадкового для дрожу (xorshift).
static inline int32_t dither_step() {
    static uint32_t s = 0x1234567u;      // будь-яке ненульове зерно
    s ^= s << 13; s ^= s >> 17; s ^= s << 5;
    // трикутний дрож амплітудою ~один крок квантування (IN_MAX/PWM_TOP):
    int32_t step = IN_MAX / PWM_TOP;                 // розмір одного вихідного рівня у масштабі входу
    int32_t a = (int32_t)(s & 0xFFFF) - 32768;       // рівномірний -32768..32767
    int32_t b = (int32_t)((s >> 16) & 0xFFFF) - 32768;
    return ((a + b) * step) / 65536;                 // сума двох рівномірних = трикутний, масштабований під крок
}

// Головна функція: один звуковий відлік -> код шпаруватості 0..PWM_TOP.
// Викликати з обробника переривання таймера на частоті вибірки.
uint16_t shape2_isr(uint16_t sample) {
    static int32_t e1 = 0, e2 = 0;

    // 1) поправка входу зворотним зв'язком: 2*e1 - e2  =  (1 - z^-1)^2
    int32_t u = (int32_t)sample + 2 * e1 - e2;

    // 2) дрож перед квантуванням — розбиває холості тони й лінеаризує квантувач
    int32_t ud = u + dither_step();

    // 3) квантування з округленням до найближчого рівня
    int32_t level = (ud * PWM_TOP + IN_MAX / 2) / IN_MAX;
    level = std::clamp(level, 0, PWM_TOP);          // насичення виходу

    // 4) похибку міряємо БЕЗ дрожу (дрож — не помилка, його повертати не треба):
    //    те, що реально віддали цим рівнем, назад у масштаб входу
    int32_t y = (level * IN_MAX + PWM_TOP / 2) / PWM_TOP;
    int32_t e = u - y;

    // 5) зсув і страхувальне обмеження станів (проти розгойдування)
    e2 = std::clamp(e1, -STATE_CLAMP, STATE_CLAMP);
    e1 = std::clamp(e,  -STATE_CLAMP, STATE_CLAMP);

    return (uint16_t)level;
}
