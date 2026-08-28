static int mode_spread(int runs, double seconds, double kfrac, double slice)
{
    if (runs < 2)  runs = 8;
    if (runs > 64) runs = 64;

    double rt_min = 1e30, rt_max = -1e30, sh_min = 1e30, sh_max = -1e30;

    printf("прогін   точна сума        user           sys      частка sys\n");
    for (int i = 1; i <= runs; i++) {
        snap a, b, d;
        take(&a);
        burn_mix(seconds, kfrac, slice);
        take(&b);
        diff(&a, &b, &d);

        double tot = d.ru_self_u + d.ru_self_s;
        double share = tot > 0.0 ? d.ru_self_s / tot : 0.0;
        printf("  %2d    %10.6f   %10.6f   %10.6f     %6.2f %%\n",
               i, d.clk_proc, d.ru_self_u, d.ru_self_s, 100.0 * share);

        if (d.clk_proc < rt_min) rt_min = d.clk_proc;
        if (d.clk_proc > rt_max) rt_max = d.clk_proc;
        if (share < sh_min) sh_min = share;
        if (share > sh_max) sh_max = share;
    }
    printf("\nточна сума: розмах %.6f с  (%.3f %% від %.3f с)\n",
           rt_max - rt_min, 100.0 * (rt_max - rt_min) / rt_min, rt_min);
    printf("частка sys: розмах %.2f відсоткового пункту (від %.2f до %.2f)\n",
           100.0 * (sh_max - sh_min), 100.0 * sh_min, 100.0 * sh_max);
    return 0;
}
