static void report(const snap& d)
{
    std::cout << "  точна сума (лічильник планувальника)\n"
              << std::fixed << std::setprecision(6)
              << "    clock_gettime(PROCESS_CPUTIME)   " << std::setw(11) << d.clk_proc << " с\n"
              << "    clock_gettime(THREAD_CPUTIME)    " << std::setw(11) << d.clk_thr << " с\n";
    if (d.sched_ok) {
        std::cout << "    /proc/self/schedstat  [0]        " << std::setw(11) << d.sched_grp << " с\n"
                  << "    /proc/thread-self/schedstat [0]  " << std::setw(11) << d.sched_thr << " с\n";
    } else {
        std::cout << "    schedstat  нема: ядро зібране без CONFIG_SCHED_INFO\n";
    }

    std::cout << "  поділ на режими (вибірка, зшита з точною сумою)\n"
              << "    getrusage(RUSAGE_SELF)     user " << std::setw(10) << d.ru_self_u
              << "  sys " << std::setw(10) << d.ru_self_s
              << "  сума " << std::setw(11) << (d.ru_self_u + d.ru_self_s) << "\n"
              << "    getrusage(RUSAGE_THREAD)   user " << std::setw(10) << d.ru_thr_u
              << "  sys " << std::setw(10) << d.ru_thr_s
              << "  сума " << std::setw(11) << (d.ru_thr_u + d.ru_thr_s) << "\n";
    if (d.stat_ok) {
        std::cout << "    /proc/self/stat 14-15      user " << std::setprecision(2)
                  << std::setw(10) << d.stat_u << "  sys " << std::setw(10) << d.stat_s
                  << "  сума " << std::setw(11) << (d.stat_u + d.stat_s)
                  << std::setprecision(0)
                  << "   (крок " << (1000.0 / clk_tck()) << " мс)\n";
    }

    double tot = d.ru_self_u + d.ru_self_s;
    std::cout << std::setprecision(6) << std::showpos
              << "  сума rusage − точна сума  " << (tot - d.clk_proc) << " с\n"
              << std::noshowpos;
    if (tot > 0.0) {
        std::cout << std::setprecision(2)
                  << "  частка sys за rusage      " << (100.0 * d.ru_self_s / tot) << " %\n";
    }
}

static int mode_mix(double seconds, double kfrac, double slice)
{
    snap a{}, b{};
    std::cout << std::fixed << std::setprecision(2)
              << "спалюємо " << seconds << " с, скибка " << (slice * 1000.0)
              << " мс, задана частка системних скибок " << std::setprecision(0)
              << (kfrac * 100.0) << " %\n";
    take(a);
    burn_mix(seconds, kfrac, slice);
    take(b);
    snap d = diff(a, b);
    report(d);
    return 0;
}
