inline int runAll(std::uint32_t seed) {
    auto &cases = registry();
    if (seed) std::shuffle(cases.begin(), cases.end(), std::mt19937{seed});

    std::size_t failed = 0;
    double      total  = 0.0;

    for (const auto &c : cases) {
        using clock = std::chrono::steady_clock;   // монотонний за означенням
        CheckFailed fail{nullptr, 0, {}};
        bool   bad = false;
        double us  = 0.0;

        const auto t0 = clock::now();
        try {
            c.body();
            us = std::chrono::duration<double, std::micro>(clock::now() - t0).count();
        } catch (const CheckFailed &e) {
            us = std::chrono::duration<double, std::micro>(clock::now() - t0).count();
            bad = true; fail = e;                  // копію робимо ПІСЛЯ засічки
        }

        std::fputs(bad ? "[FAIL] " : "[ OK ] ", stdout);
        printPadded(c.promise, 44);
        std::printf("%7.1f мкс\n", us);
        if (bad) {
            std::printf("        %s:%d: CHECK(%s)\n",
                        fail.file, fail.line, fail.what.c_str());
            ++failed;
        }
        total += us;
    }
    std::printf("\n%zu тестів, %zu провалів, %.1f мкс усього, %.2f мкс на тест\n",
                cases.size(), failed, total, total / static_cast<double>(cases.size()));
    return failed != 0;
}
