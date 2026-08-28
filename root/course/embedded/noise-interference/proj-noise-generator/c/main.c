#include <stdlib.h>
#include <math.h>

// рівномірне у (0, 1]: зсув на +1 гарантує, що нуль під ln не випаде
static double rand_0_1(void) {
    return (rand() + 1.0) / (RAND_MAX + 1.0);
}

double gauss(void) {
    static int    has_spare = 0;   // один із двох виходів кешуємо
    static double spare     = 0.0;
    if (has_spare) {
        has_spare = 0;
        return spare;              // віддаємо раніше пораховане z₂
    }
    double u1 = rand_0_1();
    double u2 = rand_0_1();
    double theta = 2.0 * M_PI * u1;
    double R     = sqrt(-2.0 * log(u2));
    spare     = R * sin(theta);    // z₂ — на потім
    has_spare = 1;
    return R * cos(theta);         // z₁ — зараз
}
