#include <string_view>

struct EngineConfig {
    int worker_threads;
    double tick_rate_hz;
    bool is_running;

    // Конструктор зобов'язаний бути constexpr
    constexpr EngineConfig(int threads, double rate)
        : worker_threads(threads), tick_rate_hz(rate), is_running(false) {}
};

// Гарантовано константна ініціалізація, але змінний стан у рантаймі:
constinit EngineConfig g_engine_config(8, 60.0);

void start_engine() {
    // Зміна дозволена, оскільки constinit не накладає константності:
    g_engine_config.is_running = true;
}
