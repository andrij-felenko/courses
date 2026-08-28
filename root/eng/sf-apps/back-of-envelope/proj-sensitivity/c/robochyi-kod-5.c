int main(void) {
    double p = point();
    double lo, hi; interval(&lo, &hi);

    int n = 100000;
    double *mc = malloc((size_t)n * sizeof *mc);
    monte_carlo(mc, n, 0);

    printf("поріг (1 сервер):     %.0f запитів/с\n", THRESHOLD);
    printf("точкова (номінал):    %.0f запитів/с   (запас x%.2f)\n", p, THRESHOLD / p);
    printf("інтервал (край-край): %.0f .. %.0f запитів/с\n", lo, hi);
    const char *side = hi <= THRESHOLD ? "весь ЛІВОРУЧ порога"
                     : lo >= THRESHOLD ? "весь ПРАВОРУЧ порога"
                     : "НАКРИВАЄ поріг";
    printf("  -> %s\n\n", side);

    double sum = 0; for (int k = 0; k < n; k++) sum += mc[k];
    printf("Монте-Карло (n=%d):\n", n);
    printf("  P50=%.0f  P90=%.0f  P95=%.0f  середнє=%.0f\n",
           pct(mc, n, 50), pct(mc, n, 90), pct(mc, n, 95), sum / n);
    printf("  P(перевищить поріг) = %.0f%%\n\n", 100 * frac_over(mc, n, THRESHOLD));

    Bar bars[NF]; tornado(bars);
    double widest = 0;
    for (int i = 0; i < NF; i++) if (bars[i].swing > widest) widest = bars[i].swing;
    if (widest == 0) widest = 1.0;
    printf("Торнадо (внесок у розкид):\n");
    for (int i = 0; i < NF; i++) {
        int len = (int)(bars[i].swing / widest * 36 + 0.5);
        char bar[37]; memset(bar, '#', (size_t)len); bar[len] = '\0';
        const char *mark = bars[i].o_lo < THRESHOLD && THRESHOLD < bars[i].o_hi
                           ? "  <-- накриває поріг" : "";
        printf("  %-10s %5.0f..%-5.0f |%-36s| Δ=%5.0f%s\n",
               bars[i].name, bars[i].o_lo, bars[i].o_hi, bar, bars[i].swing, mark);
    }
    free(mc);
    return 0;
}
