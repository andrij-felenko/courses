#include <math.h>
#include <stdio.h>

// Перевірка умови самозбудження Колпітца й запас над порогом.
// Вхід: котушка L (Гн), ємності C1,C2 (Ф), добротність контуру Q,
//       робочий струм транзистора Ic (А).
// Друкує gm·Rp, поріг C2/C1 і кратність запасу.
void colpitts_startup(float L, float C1, float C2, float Q, float Ic)
{
    const float VT = 0.026f;               // тепловий потенціал, ~26 мВ

    float Cs  = (C1 * C2) / (C1 + C2);      // послідовна ємність контуру
    float w0  = 1.0f / sqrtf(L * Cs);       // кутова частота резонансу
    float XL  = w0 * L;                     // реактивний опір котушки
    float Rp  = Q * XL;                     // паралельний опір втрат контуру

    float gm  = Ic / VT;                    // крутість у робочій точці
    float lhs = gm * Rp;                    // підсилення активної частини
    float rhs = C2 / C1;                    // плата за дільник (поріг)

    printf("f0    = %.2f МГц\n", w0 / (2.0f * (float)M_PI) / 1e6f);
    printf("Rp    = %.0f Ом,  gm = %.0f мА/В\n", Rp, 1000.0f * gm);
    printf("gm*Rp = %.1f   проти порога C2/C1 = %.2f\n", lhs, rhs);
    printf("запас = x%.1f  ->  %s\n", lhs / rhs,
           (lhs > rhs) ? "ЗАВЕДЕТЬСЯ" : "НЕ ЗАВЕДЕТЬСЯ");
}

int main(void)
{
    // L=1 мкГн, C1=C2=1 нФ, Q=80, Ic=2 мА  (контур на ~7 МГц)
    colpitts_startup(1e-6f, 1000e-12f, 1000e-12f, 80.0f, 2.0e-3f);
    return 0;
}
