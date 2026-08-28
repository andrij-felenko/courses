#include <stdint.h>

#define NBLOCK 205          // довжина блоку (про вибір — нижче)
#define FS     8000.0f      // частота дискретизації, Гц

// вісім частот: спершу чотири низькі (рядки), потім чотири високі (стовпці)
static const float dtmf_freq[8] = {
    697.0f, 770.0f, 852.0f, 941.0f,        // [0..3] — рядки
    1209.0f, 1336.0f, 1477.0f, 1633.0f     // [4..7] — стовпці
};

// таблиця символів: [рядок][стовпець]
static const char dtmf_sym[4][4] = {
    { '1', '2', '3', 'A' },
    { '4', '5', '6', 'B' },
    { '7', '8', '9', 'C' },
    { '*', '0', '#', 'D' },
};

// goertzel_power() — з кроку про алгоритм Ґерцеля
float goertzel_power(const float *x, int N, float target, float fs);

// повертає розпізнаний символ або 0, якщо тон не впізнано
char dtmf_decode(const float *x, int N)
{
    float p[8];
    for (int i = 0; i < 8; ++i)
        p[i] = goertzel_power(x, N, dtmf_freq[i], FS);

    // найсильніший бін у кожній групі
    int row = 0, col = 4;
    for (int i = 1; i < 4; ++i) if (p[i]     > p[row]) row = i;
    for (int i = 5; i < 8; ++i) if (p[i]     > p[col]) col = i;

    // ... перевірки надійності (нижче) ...

    return dtmf_sym[row][col - 4];
}
