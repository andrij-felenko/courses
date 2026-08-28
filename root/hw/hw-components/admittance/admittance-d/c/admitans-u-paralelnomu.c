// Адмітанс паралельного R||C||L на заданій частоті
#include <stdio.h>
#include <math.h>

int main(void) {
    double R = 100.0;        // Ом
    double C = 100e-9;       // Ф  (100 нФ)
    double L = 10e-3;        // Гн (10 мГн)
    double f = 2000.0;       // Гц
    double w = 2.0 * M_PI * f;       // кутова частота ω, рад/с

    double G  = 1.0 / R;             // активна провідність
    double Bc = w * C;               // ємнісна сприйнятливість (+)
    double Bl = -1.0 / (w * L);      // індуктивна сприйнятливість (−)
    double B  = Bc + Bl;             // повна реактивна частина

    double Ymag = sqrt(G*G + B*B);   // магнітуда адмітансу
    printf("G  = %.5f См\n", G);     // 0.01000 См
    printf("Bc = %.5f См\n", Bc);    // ω·C
    printf("Bl = %.5f См\n", Bl);    // -1/(ω·L)
    printf("B  = %.5f См\n", B);     // сума
    printf("|Y|= %.5f См\n", Ymag);
    return 0;
}
