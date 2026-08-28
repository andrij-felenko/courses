struct snap {
    double clk_proc = 0.0, clk_thr = 0.0;
    double ru_self_u = 0.0, ru_self_s = 0.0;
    double ru_thr_u = 0.0,  ru_thr_s = 0.0;
    double stat_u = 0.0, stat_s = 0.0;
    bool stat_ok = false;
    double sched_grp = 0.0, sched_thr = 0.0;
    bool sched_ok = false;
};

static void take(snap& k)
{
    k = snap{};
    auto [st_ok, st_val] = proc_stat_cpu("/proc/self/stat");
    k.stat_ok = st_ok;
    k.stat_u = st_val.first;
    k.stat_s = st_val.second;

    auto [sc_grp_ok, sc_grp_val] = proc_runtime("/proc/self/schedstat");
    auto [sc_thr_ok, sc_thr_val] = proc_runtime("/proc/thread-self/schedstat");
    k.sched_ok = sc_grp_ok && sc_thr_ok;
    k.sched_grp = sc_grp_val;
    k.sched_thr = sc_thr_val;

    std::tie(k.ru_self_u, k.ru_self_s) = rusage_pair(RUSAGE_SELF);
    std::tie(k.ru_thr_u,  k.ru_thr_s)  = rusage_pair(RUSAGE_THREAD);
    k.clk_proc = cpu_clock(CLOCK_PROCESS_CPUTIME_ID);
    k.clk_thr = cpu_clock(CLOCK_THREAD_CPUTIME_ID);
}

static snap diff(const snap& a, const snap& b)
{
    snap d{};
    d.clk_proc  = b.clk_proc  - a.clk_proc;
    d.clk_thr   = b.clk_thr   - a.clk_thr;
    d.ru_self_u = b.ru_self_u - a.ru_self_u;
    d.ru_self_s = b.ru_self_s - a.ru_self_s;
    d.ru_thr_u  = b.ru_thr_u  - a.ru_thr_u;
    d.ru_thr_s  = b.ru_thr_s  - a.ru_thr_s;
    d.stat_u    = b.stat_u    - a.stat_u;
    d.stat_s    = b.stat_s    - a.stat_s;
    d.sched_grp = b.sched_grp - a.sched_grp;
    d.sched_thr = b.sched_thr - a.sched_thr;
    d.stat_ok   = a.stat_ok  && b.stat_ok;
    d.sched_ok  = a.sched_ok && b.sched_ok;
    return d;
}
