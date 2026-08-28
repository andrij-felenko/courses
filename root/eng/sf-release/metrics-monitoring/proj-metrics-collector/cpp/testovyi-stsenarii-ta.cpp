void stress_test_metrics() {
    telemetry::Registry registry;
    const double bounds[] = {0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5};
    auto* hist = registry.get_histogram("http_request_duration_seconds",
                                        "handler=\"checkout\",status=\"200\"",
                                        bounds);
    auto* counter = registry.get_counter("http_requests_total",
                                         "handler=\"checkout\",status=\"200\"");

    constexpr int kThreads = 16;
    constexpr int kOpsPerThread = 100'000;
    std::vector<std::jthread> workers;

    for (int t = 0; t < kThreads; ++t) {
        workers.emplace_back([hist, counter]() {
            for (int i = 0; i < kOpsPerThread; ++i) {
                counter->inc(1);
                hist->observe(0.042); // 42 мс — потрапляє в кошик <= 0.05
            }
        });
    }

    workers.clear(); // Очікування завершення всіх потоків (join)

    // Верифікація атомарної точності
    assert(counter->get() == kThreads * kOpsPerThread);
    assert(hist->count() == kThreads * kOpsPerThread);
    assert(hist->bucket_count(3) == kThreads * kOpsPerThread); // Кошик 0.05

    std::cout << "Стрес-тест успішний: " << counter->get()
              << " операцій зафіксовано без втрат.\n";
}
