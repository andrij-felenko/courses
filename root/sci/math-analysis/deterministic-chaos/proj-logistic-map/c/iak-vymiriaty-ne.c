#include <stdio.h>
#include <math.h>

int main(void)
{
    const long N = 1000000;
    double x = 0.4, s = 0.0;

    for (long k = 0; k < N; k++) {
        s += log(fabs(4.0 * (1.0 - 2.0 * x)));   /* ln|f′| у поточній точці */
        x  = 4.0 * x * (1.0 - x);
    }
    printf("lambda = %.6f   ln2 = %.6f\n", s / N, log(2.0));
    return 0;
}
