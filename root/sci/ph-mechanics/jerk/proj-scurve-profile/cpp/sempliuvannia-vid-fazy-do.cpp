// Стан (прискорення, швидкість, положення) у момент t, 0 ≤ t ≤ total.
void scurve_at(const SCurve *s, double t, double *a, double *v, double *x) {
    if (t < 0.0)         t = 0.0;
    if (t > s->total)    t = s->total;         // після кінця — стоїмо на місці

    int k = 0;
    while (k < 6 && t >= s->t[k + 1]) k++;      // знайти активну фазу (щонайбільше 6 порівнянь)

    double tau = t - s->t[k], jk = s->j[k];
    double a0 = s->a0[k], v0 = s->v0[k], x0 = s->x0[k];
    *a = a0 + jk * tau;
    *v = v0 + a0 * tau + 0.5 * jk * tau * tau;
    *x = x0 + v0 * tau + 0.5 * a0 * tau * tau + jk * tau * tau * tau / 6.0;
}

int main(void) {
    SCurve s;
    int ok = scurve_plan(&s, 10.0, 2.0, 1.0, 1.0);   // dist=10 м, V=2, A=1, J=1
    printf("крейсер: %s   T=%.3f с   v_пік=%.3f м/с\n",
           ok ? "досягнуто" : "УРІЗАНО", s.total, s.reach);

    // самоперевірка: кінцеве положення мусить точно збігтися із замовленим ходом
    double a, v, x;
    scurve_at(&s, s.total, &a, &v, &x);
    printf("кінець: x=%.6f  v=%.6f  a=%.6f\n", x, v, a);

    for (double t = 0.0; t <= s.total + 1e-9; t += 1.0) {   // друк раз на секунду
        scurve_at(&s, t, &a, &v, &x);
        printf("t=%.1f  a=%+.3f  v=%.3f  x=%.4f\n", t, a, v, x);
    }
    return 0;
}
