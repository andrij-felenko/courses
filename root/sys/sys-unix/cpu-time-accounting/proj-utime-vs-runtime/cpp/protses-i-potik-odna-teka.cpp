struct tharg {
    double seconds = 0.0;
    double kfrac = 0.0;
    double slice = 0.001;
    double own = 0.0;
};

static int mode_threads(int n, double seconds, double kfrac)
{
    if (n < 1 || n > 16) n = 4;

    std::vector<tharg> args(n);
    std::vector<std::thread> threads;
    threads.reserve(n);

    snap a{}, b{};
    take(a);

    for (int i = 0; i < n; i++) {
        args[i].seconds = seconds;
        args[i].kfrac   = kfrac;
        args[i].slice   = 0.001;
        args[i].own     = 0.0;

        threads.emplace_back([&arg = args[i]]() {
            burn_mix(arg.seconds, arg.kfrac, arg.slice);
            arg.own = cpu_clock(CLOCK_THREAD_CPUTIME_ID);
        });
    }

    double sum = 0.0;
    for (int i = 0; i < n; i++) {
        threads[i].join();
        std::cout << std::fixed << std::setprecision(4)
                  << "потік " << i << ": CLOCK_THREAD_CPUTIME_ID   "
                  << std::setw(9) << args[i].own << " с\n";
        sum += args[i].own;
    }

    take(b);
    snap d = diff(a, b);

    std::cout << std::fixed << std::setprecision(4)
              << "\nсума по потоках                     " << std::setw(9) << sum << " с\n"
              << "CLOCK_PROCESS_CPUTIME_ID (приріст)  " << std::setw(9) << d.clk_proc << " с\n";
    if (d.stat_ok) {
        std::cout << "/proc/self/stat 14-15    (приріст)  " << std::setprecision(2)
                  << std::setw(9) << (d.stat_u + d.stat_s) << " с   ← теж уся група\n";
    }
    if (d.sched_ok) {
        std::cout << "/proc/self/schedstat     (приріст)  " << std::setprecision(4)
                  << std::setw(9) << d.sched_grp << " с   ← лише головний потік\n";
    }
    std::cout << "CLOCK_THREAD_CPUTIME_ID  (приріст)  " << std::setprecision(4)
              << std::setw(9) << d.clk_thr << " с   ← теж лише головний\n";
    return 0;
}
