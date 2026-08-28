static void report(const snap *d)
{
    printf("  точна сума (лічильник планувальника)\n");
    printf("    clock_gettime(PROCESS_CPUTIME)   %11.6f с\n", d->clk_proc);
    printf("    clock_gettime(THREAD_CPUTIME)    %11.6f с\n", d->clk_thr);
    if (d->sched_ok) {
        printf("    /proc/self/schedstat  [0]        %11.6f с\n", d->sched_grp);
        printf("    /proc/thread-self/schedstat [0]  %11.6f с\n", d->sched_thr);
    } else {
        printf("    schedstat  нема: ядро зібране без CONFIG_SCHED_INFO\n");
    }

    printf("  поділ на режими (вибірка, зшита з точною сумою)\n");
    printf("    getrusage(RUSAGE_SELF)     user %10.6f  sys %10.6f  сума %11.6f\n",
           d->ru_self_u, d->ru_self_s, d->ru_self_u + d->ru_self_s);
    printf("    getrusage(RUSAGE_THREAD)   user %10.6f  sys %10.6f  сума %11.6f\n",
           d->ru_thr_u, d->ru_thr_s, d->ru_thr_u + d->ru_thr_s);
    if (d->stat_ok)
        printf("    /proc/self/stat 14-15      user %10.2f  sys %10.2f  сума %11.2f"
               "   (крок %.0f мс)\n",
               d->stat_u, d->stat_s, d->stat_u + d->stat_s, 1000.0 / clk_tck());

    double tot = d->ru_self_u + d->ru_self_s;
    printf("  сума rusage − точна сума  %+.6f с\n", tot - d->clk_proc);
    if (tot > 0.0)
        printf("  частка sys за rusage      %.2f %%\n", 100.0 * d->ru_self_s / tot);
}

static int mode_mix(double seconds, double kfrac, double slice)
{
    snap a, b, d;
    printf("спалюємо %.2f с, скибка %.2f мс, задана частка системних скибок %.0f %%\n",
           seconds, slice * 1000.0, kfrac * 100.0);
    take(&a);
    burn_mix(seconds, kfrac, slice);
    take(&b);
    diff(&a, &b, &d);
    report(&d);
    return 0;
}
