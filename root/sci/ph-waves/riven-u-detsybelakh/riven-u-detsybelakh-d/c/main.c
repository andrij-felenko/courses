#include <math.h>
#include <stdio.h>

#define P0_SPL_PA 20.0e-6
#define V0_DBU    0.7745966692

/* Розрахунок рівня звукового тиску в дБ SPL */
double calculate_spl(double p_rms_pa) {
    if (p_rms_pa <= 0.0) return -INFINITY;
    return 20.0 * log10(p_rms_pa / P0_SPL_PA);
}

/* Розрахунок рівня напруги в dBu */
double voltage_to_dbu(double v_rms) {
    if (v_rms <= 0.0) return -INFINITY;
    return 20.0 * log10(v_rms / V0_DBU);
}

int main(void) {
    double p_talk = 0.02; /* 0.02 Па = 20 мПа (розмова) */
    double v_line = 1.228; /* 1.228 В (+4 dBu) */

    printf("Звуковий тиск %.3f Па = %.2f дБ SPL\n", p_talk, calculate_spl(p_talk));
    printf("Напруга %.3f В = %.2f dBu\n", v_line, voltage_to_dbu(v_line));
    return 0;
}
