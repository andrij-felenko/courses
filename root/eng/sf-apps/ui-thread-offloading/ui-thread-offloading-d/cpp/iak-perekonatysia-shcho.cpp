// сторожовий потік: міряє, за скільки цикл інтерфейсу забирає порожнє завдання
void watchdogLoop(std::atomic<bool>& running) {
    using clock = std::chrono::steady_clock;
    while (running.load(std::memory_order_relaxed)) {
        auto sent = clock::now();
        auto answered = std::make_shared<std::promise<clock::time_point>>();
        auto fut = answered->get_future();

        postToUiThread([answered] { answered->set_value(clock::now()); });

        if (fut.wait_for(std::chrono::seconds(2)) == std::future_status::timeout) {
            reportStall(std::chrono::milliseconds(2000), captureUiStack());
        } else {
            auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(
                          fut.get() - sent).count();
            if (ms > 50) reportStall(std::chrono::milliseconds(ms), captureUiStack());
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(200));
    }
}
