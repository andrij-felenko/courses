#define INNER_NUM 10.0    /* ходів на температуру = INNER_NUM · n^(4/3) */
#define ALPHA     0.95    /* T ← ALPHA · T                              */
#define T_EXIT    0.145   /* нижче навіть Δ = +1 не проходить            */

/* Початкова температура — не з голови, а поміряна.
   Випадкове блукання (приймаємо ВСЕ — це і є «розплав»), дивимося
   на розкид дельт: при T₀ = 20·σ типовий гірший хід проходить у 95%. */
static double init_temperature(const Netlist *nl, Placement *pl, const Grid *g,
                               Delta *d, long *cost)
{
    int want = nl->nblocks * 10;
    if (want < 1000) want = 1000;

    double sum = 0.0, sum2 = 0.0;
    int cnt = 0;
    while (cnt < want) {
        int s1 = rnd_below(g->nslots), s2 = rnd_below(g->nslots);
        if (s1 == s2) continue;
        if (pl->blk_at[s1] < 0 && pl->blk_at[s2] < 0) continue;

        int delta = swap_delta(nl, pl, g, d, s1, s2);
        *cost += delta;                      /* приймаємо все, не відкочуємо */
        sum  += delta;
        sum2 += (double)delta * (double)delta;
        cnt++;
    }
    double mean = sum / cnt;
    double var  = sum2 / cnt - mean * mean;
    return 20.0 * sqrt(var > 0.0 ? var : 0.0);
}

static void anneal(const Netlist *nl, Placement *pl, const Grid *g,
                   Delta *d, long *cost)
{
    double T = init_temperature(nl, pl, g, d, cost);
    long per_T = (long)(INNER_NUM * pow((double)nl->nblocks, 4.0 / 3.0));

    printf("T₀ = %.2f, ходів на температуру = %ld\n\n", T, per_T);

    while (T > T_EXIT) {
        long taken = 0;
        for (long m = 0; m < per_T; m++) {
            int s1 = rnd_below(g->nslots), s2 = rnd_below(g->nslots);
            if (s1 == s2) continue;
            if (pl->blk_at[s1] < 0 && pl->blk_at[s2] < 0) continue;

            int delta = swap_delta(nl, pl, g, d, s1, s2);

            if (delta <= 0 || rnd_unit() < exp(-(double)delta / T)) {
                *cost += delta;              /* лишаємо як є */
                taken++;
            } else {
                apply_swap(pl, s1, s2);      /* відкат */
            }
        }
        printf("T = %8.3f   HPWL = %6ld   прийнято %5.1f%%\n",
               T, *cost, 100.0 * (double)taken / (double)per_T);
        T *= ALPHA;
    }
}
