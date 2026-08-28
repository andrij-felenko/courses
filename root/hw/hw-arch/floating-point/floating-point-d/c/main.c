#include <stdio.h>
#include <math.h>

int main(void) {
    double a = 0.1, b = 0.2, sum = a + b;

    printf("%.17f\n", sum);          // 0.30000000000000004
    printf("%d\n", sum == 0.3);      // 0  ← НЕ рівні!

    double eps = 1e-9;
    printf("%d\n", fabs(sum - 0.3) < eps);   // 1  ← «достатньо близькі»
    return 0;
}
