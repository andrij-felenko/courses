// Приклад корутини асинхронного читача телеметрії
struct AsyncTelemetryTask {
    struct promise_type {
        AsyncTelemetryTask get_return_object() { return {}; }
        std::suspend_never initial_suspend() noexcept { return {}; }
        std::suspend_never final_suspend() noexcept { return {}; }
        void return_void() noexcept {}
        void unhandled_exception() { std::terminate(); }
    };
};

AsyncTelemetryTask poll_sensor_coroutine(std::stop_token stoken) {
    while (!stoken.stop_requested()) {
        std::cout << "[Корутина] Опитування сенсора...\n";

        // Засинаємо на 100 мс, але прокидаємося негайно у разі request_stop()
        const bool completed = co_await cancellable_sleep{std::chrono::milliseconds(100), stoken};
        if (!completed) {
            std::cout << "[Корутина] Отримано переривання під час сну! Чистий вихід.\n";
            break;
        }
    }
}
