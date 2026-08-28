#include <stdio.h>

// Перевірка: скільки різних станів проходить LFSR, поки не повернеться до зерна.
// Для максимального 16-бітного має вийти рівно 65535.
uint32_t lfsr16_period(uint16_t seed) {
    uint16_t s = seed;
    uint32_t count = 0;
    do {
        s = lfsr16_step(s);
        count++;
    } while (s != seed && count <= 0x10000u);   // страхувальний стоп
    return count;                                // очікуємо 65535
}
