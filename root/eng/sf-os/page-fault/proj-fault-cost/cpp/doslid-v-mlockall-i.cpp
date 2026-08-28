static void exp_latency(bool lock) {
    std::size_t n = 64UL * 1024 * 1024 / PGSZ;
    std::size_t len = n * PGSZ;
    std::vector<double> lat(n);

    char *p = static_cast<char*>(mmap(nullptr, len, PROT_READ | PROT_WRITE,
                                      MAP_PRIVATE | MAP_ANONYMOUS, -1, 0));
    madvise(p, len, MADV_NOHUGEPAGE);
    if (lock) {
        mlockall(MCL_CURRENT | MCL_FUTURE);
        touch_seq(p, len, true);
    }

    for (std::size_t i = 0; i < n; ++i) {
        double t0 = now();
        p[i * PGSZ] = 1;
        lat[i] = (now() - t0) * 1e6;
    }
    std::sort(lat.begin(), lat.end());
    std::cout << "  " << std::left << std::setw(24)
              << (lock ? "mlockall + прогрів" : "без mlock, перший дотик")
              << " медіана " << std::right << std::setw(6) << std::fixed << std::setprecision(2) << lat[n / 2]
              << "   99.9% " << std::setw(7) << lat[static_cast<std::size_t>(n * 0.999)]
              << "   максимум " << std::setw(8) << lat[n - 1] << " мкс\n";

    if (lock) munlockall();
    munmap(p, len);
}
