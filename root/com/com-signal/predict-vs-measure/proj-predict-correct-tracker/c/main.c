#include <stdio.h>
#include <math.h>
#include <stdint.h>

/* Стан трекера — лише два числа. */
typedef struct {
    double x;   /* оцінка положення, м */
    double p;   /* її ДИСПЕРСІЯ σ² (не σ!), м² — наскільки ми в ній непевні */
} Tracker;

/* ПЕРЕДБАЧЕННЯ: прокрутити модель на v·dt і роздути невпевненість на q. */
static void predict(Tracker *t, double v, double dt, double q) {
    t->x += v * dt;   /* модель сталої швидкості штовхає оцінку вперед */
    t->p += q;        /* світ міг зрушити непередбачувано → хмара ширшає */
}

/* КОРЕКЦІЯ: підтягнути оцінку до виміру z (дисперсія r); вернути підсилення K. */
static double correct(Tracker *t, double z, double r) {
    double K = t->p / (t->p + r);   /* відносна певність, 0..1 */
    t->x += K * (z - t->x);         /* x + K·(вимір − передбачення) */
    t->p = (1.0 - K) * t->p;        /* хмара звузилась */
    return K;
}

/* --- крихітний детермінований ГВЧ + гаусів шум, щоб приклад відтворювався --- */
static uint64_t rng = 0x2545F4914F6CDD1DULL;
static double urand(void) {                 /* рівномірне (0,1] */
    rng ^= rng << 13; rng ^= rng >> 7; rng ^= rng << 17;
    return ((rng >> 11) + 1.0) * (1.0 / 9007199254740992.0);
}
static double gauss(double sigma) {         /* Бокс–Мюллер: N(0, σ²) */
    double u1 = urand(), u2 = urand();       /* послідовно: спершу u1, потім u2 */
    return sigma * sqrt(-2.0 * log(u1)) * cos(6.283185307179586 * u2);
}

int main(void) {
    const double dt = 1.0, v = 1.0;         /* такт 1 с, відома швидкість 1 м/с */
    const double q  = 0.25, r = 9.0;        /* ДИСПЕРСІЇ шуму процесу й виміру */
    const double sig_proc = 0.5, sig_meas = 3.0;   /* їхні σ: q=σ², r=σ² */
    const int    N = 100;

    double  x_true = 0.0;                    /* істина стартує в 0 */
    Tracker t = { -20.0, 100.0 };            /* навмисне ХИБНИЙ старт, велика p */
    double  x_dead = t.x;                    /* «самий прогноз»: трекер без корекцій */
    double  se_t = 0, se_r = 0, se_d = 0;    /* суми квадратів похибок */

    for (int k = 1; k <= N; k++) {
        x_true += v * dt + gauss(sig_proc);        /* істина: швидкість + поштовхи */
        double z = x_true + gauss(sig_meas);        /* зашумлений вимір давача */

        predict(&t, v, dt, q);                      /* ← передбач */
        double K = correct(&t, z, r);               /* ← виправ  */
        x_dead += v * dt;                           /* прогноз без корекцій дрейфує */

        se_t += (t.x   - x_true) * (t.x   - x_true);
        se_r += (z     - x_true) * (z     - x_true);
        se_d += (x_dead- x_true) * (x_dead- x_true);

        if (k <= 6) printf("k=%d  K=%.3f  p=%.3f\n", k, K, t.p);
    }
    printf("RMS: трекер=%.2f  вимір=%.2f  прогноз=%.2f (м)\n",
           sqrt(se_t / N), sqrt(se_r / N), sqrt(se_d / N));
    return 0;
}
