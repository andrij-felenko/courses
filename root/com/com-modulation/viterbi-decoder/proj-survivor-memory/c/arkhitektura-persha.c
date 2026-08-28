typedef struct {
    unsigned dec[D][S];   /* кільце з D колонок; колонка — по біту рішення на стан */
    int      metric[S];
    int      t;           /* скільки тактів опрацьовано */
} tb_smu;

static void tb_init(tb_smu *q) {
    q->t = 0;
    q->metric[0] = 0;                                 /* старт відомий — стан 00 */
    for (unsigned s = 1; s < S; s++) q->metric[s] = INT_MAX;
}

/* Подати прийняту пару; повертає 1 і кладе біт у *out, якщо цього такту є видача. */
static int tb_step(tb_smu *q, int r0, int r1, int *out) {
    int nm[S];
    acs(q->metric, nm, q->dec[q->t % D], r0, r1);     /* нову колонку — одразу в кільце */
    memcpy(q->metric, nm, sizeof nm);
    q->t++;
    if (q->t < D) return 0;                           /* вікно ще не повне — warm-up */

    unsigned s = (unsigned) best(q->metric);          /* старт простеження — найкращий стан */
    for (int k = 0; k < D - 1; k++) {                 /* крок назад крізь вікно */
        unsigned col = (unsigned)(q->t - 1 - k) % D;
        s = ((s & LOW) << 1) | q->dec[col][s];        /* відновити попередника з біта рішення */
    }
    *out = (int)(s >> (NU - 1));                      /* найдавніший вхідний біт вікна */
    return 1;
}
