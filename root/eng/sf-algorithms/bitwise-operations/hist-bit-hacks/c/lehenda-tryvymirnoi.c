#include <stdint.h>
#include <string.h>

float fast_inv_sqrt(float number) {
    int32_t i;
    float x2, y;
    x2 = number * 0.5f;
    y  = number;
    memcpy(&i, &y, sizeof(i));                  // безпечне копіювання бітів без strict aliasing
    i  = 0x5f3759df - (i >> 1);                 // магічний бітовий зсув
    memcpy(&y, &i, sizeof(y));
    y  = y * (1.5f - (x2 * y * y));             // 1 ітерація методу Ньютона-Рафсона
    return y;
}
