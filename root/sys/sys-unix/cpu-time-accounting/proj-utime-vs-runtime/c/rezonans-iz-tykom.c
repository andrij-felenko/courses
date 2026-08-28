/* Ті самі умови, різна довжина скибки. Одне зі значень збігається з періодом
   тику ядра — і саме на ньому поділ перестає бути схожим на сусідів. */
static int mode_phase(double seconds, double kfrac)
{
    static const double slices_ms[] = { 0.2, 1.0, 2.0, 4.0, 8.0, 10.0 };

    printf("скибка    частка sys    точна сума\n");
    for (size_t i = 0; i < sizeof slices_ms / sizeof slices_ms[0]; i++) {
        snap a, b, d;
        take(&a);
        burn_mix(seconds, kfrac, slices_ms[i] / 1000.0);
        take(&b);
        diff(&a, &b, &d);

        double tot = d.ru_self_u + d.ru_self_s;
        printf("%5.1f мс     %6.2f %%     %10.6f\n",
               slices_ms[i], tot > 0.0 ? 100.0 * d.ru_self_s / tot : 0.0, d.clk_proc);
    }
    return 0;
}
