// Обернення Z = R + jX  →  Y = G + jB  (фірмварний обчислювач)
#include <stdio.h>

int main(void) {
    double R = 30.0, X = 40.0;          // Ом: активний опір та реактивність
    double den = R*R + X*X;             // R² + X²  = 900 + 1600 = 2500
    double G = R / den;                 // активна провідність, См
    double B = -X / den;                // сприйнятливість, См

    printf("|Z| = %.1f Ом\n", 50.0);    // sqrt(2500) = 50
    printf("G = %.4f См\n", G);          // 30/2500  = 0.0120 См
    printf("B = %.4f См\n", B);          // -40/2500 = -0.0160 См
    return 0;
}
