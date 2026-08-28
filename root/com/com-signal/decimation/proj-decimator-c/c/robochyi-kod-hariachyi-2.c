int main(void)
{
    const int    M  = 4;
    const double fs = 48000.0;          /* Гц */
    const int    K  = 4096;             /* вхідних відліків на прогін */
    decim_t d;
    q15_t   y;
    int     n, t;

    /* (1) робота: множень на вихід */
    long outs       = K / M;
    long muls_smart = outs * (long)TAPS;        /* лише виживші виходи */
    long muls_naive = (long)K * TAPS;           /* КІХ на кожному вході */
    printf("вхід %d відліків, M=%d, відводів=%d\n", K, M, TAPS);
    printf("наївно:  %ld множень\n", muls_naive);
    printf("розумно: %ld множень  (×%.1f менше)\n",
           muls_smart, (double)muls_naive / muls_smart);

    /* (2) чи глушиться високий тон? 2 кГц має пройти, 9 кГц (> 6 кГц) — згаснути */
    double freqs[2] = { 2000.0, 9000.0 };
    for (t = 0; t < 2; t++) {
        decim_init(&d, M);
        int peak = 0;
        for (n = 0; n < K; n++) {
            double s = 0.7 * sin(2.0 * M_PI * freqs[t] * n / fs);
            if (decim_put(&d, to_q15(s), &y)) {
                int a = (y < 0) ? -y : y;
                if (n > K / 2 && a > peak) peak = a;    /* заміряємо після розігріву */
            }
        }
        printf("тон %.0f Гц: пік виходу %.3f\n", freqs[t], peak / 32768.0);
    }
    return 0;
}
