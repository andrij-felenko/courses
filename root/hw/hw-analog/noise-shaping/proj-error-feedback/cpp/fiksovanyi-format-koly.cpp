#include <cstdint>

constexpr int DROP    = 8;                        // скільки молодших бітів відкидаємо (16 -> 8)
constexpr int OUT_MAX = (1 << (16 - DROP)) - 1;   // 255 для 8-бітного виходу

uint8_t shape2_shift(uint16_t sample) {
    static int32_t e1 = 0, e2 = 0;

    int32_t u = (int32_t)sample + 2 * e1 - e2;

    // округлення до найближчого рівня = додати півкроку (1<<(DROP-1)) і відкинути DROP біт
    int32_t level = (u + (1 << (DROP - 1))) >> DROP;
    if (level < 0)        level = 0;
    if (level > OUT_MAX)  level = OUT_MAX;

    int32_t y = level << DROP;        // назад у масштаб входу — просто зсув
    int32_t e = u - y;

    e2 = e1;
    e1 = e;

    return (uint8_t)level;
}
