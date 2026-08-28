#include <cstdint>

constexpr int32_t PWM_TOP =   500;
constexpr int32_t IN_MAX  = 65535;

// Формувач шуму 2-го порядку. NTF = (1 - z^-1)^2.
uint16_t shape2(uint16_t sample) {
    static int32_t e1 = 0, e2 = 0;       // дві останні похибки (масштаб входу)

    // поправка входу: 2*e1 - e2  (розкриті дужки (1 - z^-1)^2)
    int32_t u = (int32_t)sample + 2 * e1 - e2;

    int32_t level = (u * PWM_TOP + IN_MAX / 2) / IN_MAX;
    if (level < 0)       level = 0;
    if (level > PWM_TOP) level = PWM_TOP;

    int32_t y = (level * IN_MAX + PWM_TOP / 2) / PWM_TOP;
    int32_t e = u - y;                   // нова похибка

    e2 = e1;                             // ЗСУВ станів: спершу старе
    e1 = e;                              // тоді нове

    return (uint16_t)level;
}
