#include <stdio.h>
#include <math.h>

// Повна картина послідовного RLC-резонансу з L, C, R.
// L у генрі, C у фарадах, R — повний послідовний опір втрат (Ом).
typedef struct {
    float w0;      // кутова резонансна частота, рад/с
    float f0;      // резонансна частота, Гц
    float X0;      // реактивний опір елемента на резонансі (XL = Xc), Ом
    float Q;       // добротність
    float bw;      // смуга −3 дБ, Гц
} Resonance;

Resonance series_rlc(float L, float C, float R) {
    Resonance r;
    r.w0 = 1.0f / sqrtf(L * C);              // ω₀ = 1/√(LC)
    r.f0 = r.w0 / (2.0f * (float)M_PI);
    r.X0 = r.w0 * L;                         // = 1/(ω₀C) на резонансі
    r.Q  = r.X0 / R;                         // Q = ω₀L/R
    r.bw = r.f0 / r.Q;                       // Δf = f₀/Q = R/(2πL)
    return r;
}

// Точне значення |Z| на ДОВІЛЬНІЙ частоті — те, з чого все виведено.
float z_mag(float L, float C, float R, float w) {
    float X = w * L - 1.0f / (w * C);        // реактивність XL − Xc
    return sqrtf(R * R + X * X);             // |Z| = √(R² + X²)
}

int main(void) {
    float L = 100e-6f, C = 250e-12f, R = 12.0f, U = 1.0f;
    Resonance r = series_rlc(L, C, R);

    float Imax = U / R;                      // струм на резонансі
    float Umag = r.Q * U;                    // напруга на L і C: Q·U

    printf("f0   = %.3f МГц\n", r.f0 / 1e6f);
    printf("|Z|0 = %.1f Ом  (= R, мінімум)\n", z_mag(L, C, R, r.w0));
    printf("Imax = %.0f мА\n", Imax * 1000.0f);
    printf("X0   = %.0f Ом   (XL = Xc на резонансі)\n", r.X0);
    printf("Q    = %.1f\n", r.Q);
    printf("U_L = U_C = %.1f В   (з U = %.0f В на вході)\n", Umag, U);
    printf("смуга −3 дБ = %.1f кГц\n", r.bw / 1e3f);
    return 0;
}
/* Очікуваний вивід:
   f0   = 1.006 МГц
   |Z|0 = 12.0 Ом  (= R, мінімум)
   Imax = 83 мА
   X0   = 632 Ом   (XL = Xc на резонансі)
   Q    = 52.7
   U_L = U_C = 52.7 В   (з U = 1 В на вході)
   смуга −3 дБ = 19.1 кГц
*/
