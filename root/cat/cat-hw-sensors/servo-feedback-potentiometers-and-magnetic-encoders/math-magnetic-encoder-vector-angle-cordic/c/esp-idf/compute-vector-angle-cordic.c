#include <stdint.h>
#include <math.h>

// Таблиця кутів arctan(2^-i) у фіксованій крапці (формат Q1.15, де 32768 = pi)
static const int16_t cordic_ctab[] = {
    8192, 4836, 2555, 1297, 651, 326, 163, 81, 41, 20, 10, 5, 2, 1
};

// Обчислення кута в діапазоні [0, 65535] (Q16 від 0 до 360 градусів)
uint16_t compute_vector_angle_cordic(int16_t cos_raw, int16_t sin_raw) {
    int32_t x = cos_raw;
    int32_t y = sin_raw;
    int32_t z = 0;

    // Крок 1. Приведення вектора до I або IV квадранта
    if (x < 0) {
        x = -cos_raw;
        y = -sin_raw;
        z = (y >= 0) ? 32768 : -32768; // додавання/віднімання pi
    }

    // Крок 2. Ітерації CORDIC методом побітових зсувів
    for (int i = 0; i < 14; i++) {
        int32_t d = (y < 0) ? 1 : -1;
        int32_t x_next = x - d * (y >> i);
        int32_t y_next = y + d * (x >> i);
        z -= d * cordic_ctab[i];
        x = x_next;
        y = y_next;
    }

    // Масштабування з діапазону [-pi, pi] у [0, 65535]
    return (uint16_t)((z < 0) ? (z + 65536) : z);
}
