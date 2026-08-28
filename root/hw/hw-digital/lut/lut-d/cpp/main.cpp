#include <stdint.h>
#include <math.h>

#define N 256                       // вузлів на повний оберт 2π
static float SIN_LUT[N];            // 256·4 = 1024 байти у Flash/RAM

// один раз на старті: порахувати дорогий sinf() наперед
void sin_lut_init(void) {
    for (int i = 0; i < N; i++)
        SIN_LUT[i] = sinf(2.0f * (float)M_PI * i / N);
}

// гарячий шлях: жодного sinf() — лише читання + одне множення
float sin_fast(float rad) {
    float x = rad * (N / (2.0f * (float)M_PI));   // радіани → позиція в таблиці
    int   i = (int)x;                              // лівий вузол
    float f = x - i;                               // дробова частина: 0..1
    float a = SIN_LUT[i & (N - 1)];                // & (N-1): дешеве "mod 256"
    float b = SIN_LUT[(i + 1) & (N - 1)];          // правий вузол
    return a + (b - a) * f;                         // пряма між a і b
}
