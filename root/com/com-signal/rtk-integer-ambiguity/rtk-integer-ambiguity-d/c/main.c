#include <stdio.h>

#define LAMBDA_L1 0.190293f   /* довжина хвилі GPS L1, метри */

/* Відстань уздовж променя за цілим N і виміряною дробовою фазою phi (у циклах). */
float range_from_phase(long N, float phi_cycles)
{
    return (N + phi_cycles) * LAMBDA_L1;
}

int main(void)
{
    long  N_true = 128;        /* справжнє число цілих хвиль */
    float phi    = 0.37f;      /* дробова частина, виміряна точно */

    float r_true = range_from_phase(N_true,     phi);
    float r_off1 = range_from_phase(N_true + 1, phi);   /* схибили на 1 цикл */
    float r_off3 = range_from_phase(N_true - 3, phi);   /* схибили на 3 цикли */

    printf("правильно:      %.4f m\n", r_true);
    printf("помилка +1:     %.4f m  (зсув %.1f cm)\n",
           r_off1, (r_off1 - r_true) * 100.0f);
    printf("помилка -3:     %.4f m  (зсув %.1f cm)\n",
           r_off3, (r_off3 - r_true) * 100.0f);
    return 0;
}
