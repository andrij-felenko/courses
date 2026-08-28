#include <stdio.h>
#include <math.h>

static double f(double x) { return 4.0 * x * (1.0 - x); }

int main(void)
{
    double a = 0.400000000;          /* старт A */
    double b = 0.400000001;          /* старт B — на 1e-9 далі */

    for (int n = 0; n <= 45; n++) {
        double d = fabs(a - b);
        printf("n=%2d  A=%.9f  B=%.9f  |A-B|=%.3e  log2=%6.2f\n",
               n, a, b, d, log2(d));
        a = f(a);
        b = f(b);
    }
    return 0;
}
