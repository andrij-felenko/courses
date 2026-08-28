#include <stdio.h>

int main(void) {
    double Vdd = 3.3;        // В
    double C   = 200e-12;    // Ф  (200 пФ)
    double R   = 4700.0;     // Ом
    double t_allowed = 300e-9; // с  — межа фронту для Fast-mode I2C

    // Фронт HIGH міряють між 0.3·VDD і 0.7·VDD (як у даташиті I2C).
    // Для згасальної експоненти V=VDD(1−e^(−t/RC)) цей відрізок triває ≈ 0.847·R·C.
    double tau   = R * C;                 // стала часу RC
    double t_rise = 0.847 * tau;          // час фронту 30%→70%

    printf("RC = %.0f ns\n", tau * 1e9);
    printf("фронт резистора (30-70%%) = %.0f ns\n", t_rise * 1e9);
    printf("дозволено стандартом      = %.0f ns\n", t_allowed * 1e9);
    printf(t_rise <= t_allowed ? ">> резистор ВСТИГАЄ\n"
                               : ">> резистор НЕ встигає — треба менший R або прискорювач\n");
    return 0;
}
