/* C: той самий цикл, але гарячий шлях у машинних інструкціях — для великих N */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

/* xorshift64 — дешевий і достатньо якісний ГВЧ для Монте-Карло */
static uint64_t st = 1;
static inline double urand(void) {
    st ^= st << 13; st ^= st >> 7; st ^= st << 17;
    return (st >> 11) * (1.0 / 9007199254740992.0);   /* 53 біти в [0,1) */
}

int main(int argc, char **argv) {
    double   p      = atof(argv[1]);
    long long target = argc > 2 ? atoll(argv[2]) : 100;
    st = argc > 3 ? strtoull(argv[3], 0, 10) : 1;     /* зерно, тільки не 0 */

    long long errors = 0, trials = 0;
    while (errors < target) {
        int flips = (urand() < p) + (urand() < p) + (urand() < p);
        errors += (flips >= 2);        /* помилка ⟺ ≥2 перевороти з 3 */
        trials++;
    }
    printf("p=%.4g  p_hat=%.3e  прогонів=%lld  теорія=%.3e\n",
           p, (double)errors / trials, trials, 3*p*p - 2*p*p*p);
    return 0;
}
