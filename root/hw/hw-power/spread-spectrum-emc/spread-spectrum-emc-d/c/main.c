#include <stdio.h>
#include <math.h>

int main(void) {
    double fsw      = 440e3;    // частота перемикання, Гц
    int    harm     = 3;        // проблемна гармоніка
    double spread   = 0.06;     // ±6 % розмаху
    double rbw      = 9e3;      // вікно приймача CISPR 25 (низька смуга), Гц

    double f_harm = harm * fsw;             // 1.32 МГц — де стоїть спиця
    double df     = 2.0 * spread * f_harm;  // повна ширина розмазу (±6 % → 12 %)
    double gain   = 10.0 * log10(df / rbw); // наближене падіння піку

    printf("гармоніка : %.2f МГц\n", f_harm / 1e6);
    printf("розмаз Δf  : %.0f кГц (%.0f %% від гармоніки)\n",
           df / 1e3, 2 * spread * 100);
    printf("вікно RBW  : %.0f кГц\n", rbw / 1e3);
    printf("падіння піку ~ %.1f дБ\n", gain);

    double before = -8.0;                   // було: на 8 дБ ВИЩЕ стелі
    double after  = before + gain;
    printf("запас до стелі: %.1f -> %.1f дБ  %s\n",
           before, after, after > 0 ? "(проходить)" : "(усе ще завалено)");
    return 0;
}
