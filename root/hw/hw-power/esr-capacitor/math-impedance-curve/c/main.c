// Параметри реального конденсатора → точки галочки |Z(f)|.
// f0 — дно (резонанс), |Z|min = ESR, плюс DF і Q на заданій частоті.
#include <stdio.h>
#include <math.h>

// модуль повного опору в одній точці частоти: |Z| = sqrt(ESR^2 + (wL - 1/wC)^2)
double z_mag(double f, double C, double L, double esr) {
    double w  = 2.0 * M_PI * f;
    double X  = w * L - 1.0 / (w * C);   // чиста реактивність: індуктивна − ємнісна
    return sqrt(esr * esr + X * X);
}

int main(void) {
    double C = 100e-9;        // 100 нФ
    double L = 2e-9;          // 2 нГ паразитної індуктивності
    double esr = 0.03;        // 0.03 Ом
    double f_work = 100e3;    // робоча частота 100 кГц

    double f0 = 1.0 / (2.0 * M_PI * sqrt(L * C));   // дно галочки
    double Xc = 1.0 / (2.0 * M_PI * f_work * C);    // ємнісний опір на 100 кГц
    double DF = esr / Xc;                            // коефіцієнт втрат
    double Q  = Xc / esr;                            // добротність = 1/DF

    printf("f0      = %.2f MHz\n", f0 / 1e6);
    printf("|Z|@f0  = %.3f Ohm  (= ESR)\n", z_mag(f0, C, L, esr));
    printf("|Z|@100kHz = %.2f Ohm\n",       z_mag(f_work, C, L, esr));
    printf("DF      = %.5f\n", DF);
    printf("Q       = %.0f\n", Q);
    return 0;
}
