struct tharg { double seconds, kfrac, slice, own; };

static void *thread_body(void *p)
{
    struct tharg *a = p;
    burn_mix(a->seconds, a->kfrac, a->slice);
    a->own = cpu_clock(CLOCK_THREAD_CPUTIME_ID);
    return NULL;
}

static int mode_threads(int n, double seconds, double kfrac)
{
    if (n < 1 || n > 16) n = 4;

    pthread_t th[16];
    struct tharg arg[16];
    snap a, b, d;

    take(&a);
    for (int i = 0; i < n; i++) {
        arg[i].seconds = seconds;
        arg[i].kfrac   = kfrac;
        arg[i].slice   = 0.001;
        arg[i].own     = 0.0;
        if (pthread_create(&th[i], NULL, thread_body, &arg[i]) != 0) {
            perror("pthread_create");
            return 1;
        }
    }

    double sum = 0.0;
    for (int i = 0; i < n; i++) {
        pthread_join(th[i], NULL);
        printf("потік %d: CLOCK_THREAD_CPUTIME_ID   %9.4f с\n", i, arg[i].own);
        sum += arg[i].own;
    }
    take(&b);
    diff(&a, &b, &d);

    printf("\nсума по потоках                     %9.4f с\n", sum);
    printf("CLOCK_PROCESS_CPUTIME_ID (приріст)  %9.4f с\n", d.clk_proc);
    if (d.stat_ok)
        printf("/proc/self/stat 14-15    (приріст)  %9.2f с   ← теж уся група\n",
               d.stat_u + d.stat_s);
    if (d.sched_ok)
        printf("/proc/self/schedstat     (приріст)  %9.4f с   ← лише головний потік\n",
               d.sched_grp);
    printf("CLOCK_THREAD_CPUTIME_ID  (приріст)  %9.4f с   ← теж лише головний\n",
           d.clk_thr);
    return 0;
}
