typedef struct {
    double clk_proc, clk_thr;          /* точна сума: процес і потік        */
    double ru_self_u, ru_self_s;       /* поділ: процес                     */
    double ru_thr_u,  ru_thr_s;        /* поділ: потік                      */
    double stat_u, stat_s;   int stat_ok;
    double sched_grp, sched_thr; int sched_ok;
} snap;

static void take(snap *k)
{
    memset(k, 0, sizeof *k);
    k->stat_ok  = (proc_stat_cpu("/proc/self/stat", &k->stat_u, &k->stat_s) == 0);
    k->sched_ok = (proc_runtime("/proc/self/schedstat",        &k->sched_grp) == 0)
               && (proc_runtime("/proc/thread-self/schedstat", &k->sched_thr) == 0);
    rusage_pair(RUSAGE_SELF,   &k->ru_self_u, &k->ru_self_s);
    rusage_pair(RUSAGE_THREAD, &k->ru_thr_u,  &k->ru_thr_s);
    k->clk_proc = cpu_clock(CLOCK_PROCESS_CPUTIME_ID);
    k->clk_thr  = cpu_clock(CLOCK_THREAD_CPUTIME_ID);
}

static void diff(const snap *a, const snap *b, snap *d)
{
    d->clk_proc  = b->clk_proc  - a->clk_proc;
    d->clk_thr   = b->clk_thr   - a->clk_thr;
    d->ru_self_u = b->ru_self_u - a->ru_self_u;
    d->ru_self_s = b->ru_self_s - a->ru_self_s;
    d->ru_thr_u  = b->ru_thr_u  - a->ru_thr_u;
    d->ru_thr_s  = b->ru_thr_s  - a->ru_thr_s;
    d->stat_u    = b->stat_u    - a->stat_u;
    d->stat_s    = b->stat_s    - a->stat_s;
    d->sched_grp = b->sched_grp - a->sched_grp;
    d->sched_thr = b->sched_thr - a->sched_thr;
    d->stat_ok   = a->stat_ok  && b->stat_ok;
    d->sched_ok  = a->sched_ok && b->sched_ok;
}
