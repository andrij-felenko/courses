int main() {
    CanaryTrafficArbiter::Config cfg{
        .initial_weight_pct = 10,       // 10% на канарку
        .max_error_rate_delta = 0.01,   // Макс +1% помилок
        .max_p99_latency_us = 100'000,
        .eval_interval = std::chrono::milliseconds(200)
    };

    CanaryTrafficArbiter arbiter(cfg, [](std::string_view reason, double c_err, double b_err) {
        std::cout << "[ALERT] Надіслано PagerDuty алерту черговому SRE: " << reason << "\n";
    });

    std::cout << "Старт маршрутизації: початкова вага = " << arbiter.get_current_weight() << "%\n";

    // Емуляція 1000 нормальних запитів
    for (int i = 0; i < 1000; ++i) {
        std::string uid = "user_" + std::to_string(i);
        auto target = arbiter.route_request(uid);
        // Затримка 15мс, помилок немає
        arbiter.record_outcome(target, 15'000, false);
    }

    std::this_thread::sleep_for(std::chrono::milliseconds(300));
    std::cout << "Після нормального потоку: вага = " << arbiter.get_current_weight() << "%\n";

    // Емуляція деградації канарки: 20% помилок 500 на канарковому вузлі
    for (int i = 1000; i < 1500; ++i) {
        std::string uid = "user_" + std::to_string(i);
        auto target = arbiter.route_request(uid);
        if (target == CanaryTrafficArbiter::TargetVariant::Canary) {
            arbiter.record_outcome(target, 45'000, (i % 5 == 0)); // 20% помилок на канарці
        } else {
            arbiter.record_outcome(target, 15'000, false);
        }
    }

    std::this_thread::sleep_for(std::chrono::milliseconds(400));
    std::cout << "Після збою: поточна вага канарки = " << arbiter.get_current_weight() << "%\n";

    return 0;
}
