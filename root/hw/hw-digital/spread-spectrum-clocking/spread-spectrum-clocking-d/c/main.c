#include <stdio.h>
#include <math.h>

int main(void) {
    double f0        = 100e6;    // такт, Гц
    int    harmonic  = 5;        // проблемна гармоніка
    double spread    = 0.005;    // 0.5 %  розмаз униз
    double rbw       = 120e3;    // вікно приймача CISPR, Гц

    double f_harm  = harmonic * f0;          // 500 МГц — де стоїть спиця
    double df      = spread * f_harm;        // абсолютний обшир розмазу на цій гармоніці
    double gain_dB = 10.0 * log10(df / rbw); // наближене падіння піку

    printf("гармоніка : %.0f МГц\n", f_harm / 1e6);
    printf("розмаз Δf  : %.2f МГц (%.1f %% від гармоніки)\n", df / 1e6, spread * 100);
    printf("вікно RBW  : %.0f кГц\n", rbw / 1e3);
    printf("падіння піку ~ %.1f дБ\n", gain_dB);

    double margin_before = -6.0;             // було: на 6 дБ ВИЩЕ межі
    double margin_after  = margin_before + gain_dB;
    printf("запас до межі: %.1f дБ → %.1f дБ  %s\n",
           margin_before, margin_after,
           margin_after > 0 ? "(проходить)" : "(усе ще завалено)");
    return 0;
}
