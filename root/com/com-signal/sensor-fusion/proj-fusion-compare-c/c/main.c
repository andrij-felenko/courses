#include <stdio.h>
#include <math.h>
#include <stdint.h>

#define PI   3.14159265358979323846
#define DT   0.01     /* крок, с (100 Гц)                */
#define Q    0.001    /* шум моделі, град² за такт        */
#define R    9.0      /* шум акселерометра, град² (σ = 3°) */
#define BIAS 1.0      /* сталий зсув нуля гіроскопа, град/с */

/* усталений коефіцієнт Калмана — корінь рівняння рівноваги */
static double kalman_gain_inf(void) {
    double Pm = (Q + sqrt(Q*Q + 4.0*Q*R)) / 2.0;   /* стала дисперсія передбачення */
    return Pm / (Pm + R);
}

/* відтворюваний шум: 31-бітний LCG + перетворення Бокса–Мюллера */
static uint32_t rng = 2026u;
static double urand(void) {                        /* рівномірне [0,1) */
    rng = (1103515245u*rng + 12345u) & 0x7fffffffu;
    return rng / 2147483648.0;
}
static double gauss(double sigma) {                /* вибірка з N(0, σ²) */
    double u1 = urand(), u2 = urand();
    if (u1 < 1e-12) u1 = 1e-12;                     /* log(0) заборонено */
    return sigma * sqrt(-2.0*log(u1)) * cos(2.0*PI*u2);
}

/* синтез: істинний кут і його похідна — кутова швидкість */
static double true_angle(double t) { return 20.0*sin(2.0*PI*0.2*t); }
static double true_rate (double t) { return 20.0*2.0*PI*0.2*cos(2.0*PI*0.2*t); }

int main(void) {
    const double Kinf  = kalman_gain_inf();
    const double alpha = 1.0 - Kinf;               /* комплементарний бере це число */
    printf("K_inf = %.7f   alpha = 1-K_inf = %.7f   1-alpha = %.7f\n\n",
           Kinf, alpha, 1.0 - alpha);

    /* ── Фаза A: коефіцієнт сходиться сам, без жодного виміру ── */
    printf("phase A: gain convergence (data-independent)\n");
    printf("   n          P-           K\n");
    double P = 900.0;                              /* σ₀ = 30°: про кут нічого не відомо */
    for (int n = 1; n <= 1200; ++n) {
        double Pm = P + Q;                         /* передбачення розширює дисперсію */
        double K  = Pm / (Pm + R);                 /* оновлення: частка довіри виміру */
        P = (1.0 - K) * Pm;                        /* вимір стягує дисперсію */
        if (n==1||n==2||n==3||n==5||n==10||n==20||n==50||n==100||n==200||n==500)
            printf("%4d  %11.6f  %11.7f\n", n, Pm, K);
    }
    printf("  ... -> K_inf = %.7f\n\n", Kinf);

    /* ── Фаза B: заморожений Калман = комплементарний, буква в букву ── */
    printf("phase B: same signal, equal start, Kalman gain frozen at K_inf\n");
    printf("   n     theta_comp   theta_kalman       diff\n");
    double th_c = true_angle(0.0) + gauss(3.0);    /* спільний старт: перший відлік акселя */
    double th_k = th_c;
    double Pk = (Q + sqrt(Q*Q + 4.0*Q*R)) / 2.0 - Q;   /* Pk+Q = P⁻∞  →  K ≡ K_inf */
    double maxd = 0.0;
    for (int n = 1; n <= 500; ++n) {
        double t = n * DT;
        double w = true_rate(t) + BIAS;            /* гіроскоп: швидкість + зсув */
        double z = true_angle(t) + gauss(3.0);     /* акселерометр: кут + шум  */

        th_c = alpha*(th_c + w*DT) + (1.0 - alpha)*z;   /* комплементарний */

        double thm = th_k + w*DT;                  /* Калман — predict */
        double Pm  = Pk + Q;
        double K   = Pm / (Pm + R);                /* Калман — update  */
        th_k = thm + K*(z - thm);
        Pk   = (1.0 - K) * Pm;

        double d = th_k - th_c;
        if (fabs(d) > maxd) maxd = fabs(d);
        if (n==1||n==2||n==10||n==100||n==500)
            printf("%4d  %11.6f  %11.6f  %10.2e\n", n, th_c, th_k, d);
    }
    printf("  max |theta_kalman - theta_comp| = %.2e  (last bit of double)\n", maxd);
    return 0;
}
