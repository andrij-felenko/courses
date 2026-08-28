#include <stdint.h>

// Оригінальний код Джона Кармака (UB через Strict Aliasing у C99/C11)
float Q_rsqrt(float number) {
    long i;
    float x2, y;
    const float threehalfs = 1.5F;

    x2 = number * 0.5F;
    y  = number;
    i  = * ( long * ) &y;                       // Злий трюк приведення вказівників (UB!)
    i  = 0x5f3759df - ( i >> 1 );               // Початкове наближення
    y  = * ( float * ) &i;                      // Зворотне приведення (UB!)
    y  = y * ( threehalfs - ( x2 * y * y ) );   // 1-ша ітерація методу Ньютона-Рафсона

    return y;
}
