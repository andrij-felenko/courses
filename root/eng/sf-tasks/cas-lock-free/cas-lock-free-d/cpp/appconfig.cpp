#include <iostream>
#include <memory>
#include <atomic>
#include <string>

// Незмінна структура складеного стану
struct AppConfig {
    const std::string host;
    const int port;
    const int max_connections;

    AppConfig(std::string h, int p, int m) 
        : host(std::move(h)), port(p), max_connections(m) {}
};

class ConfigManager {
private:
    // Атомарний вказівник на shared_ptr забезпечує безпечне керування пам'яттю
    std::atomic<std::shared_ptr<const AppConfig>> config_;

public:
    explicit ConfigManager(std::shared_ptr<const AppConfig> initial) 
        : config_(std::move(initial)) {}

    // Зчитування стану без блокувань
    std::shared_ptr<const AppConfig> get_config() const {
        return config_.load(std::memory_order_acquire);
    }

    // Атомарна підміна стану за схемою Copy-on-Write та CAS
    void update_port(int new_port) {
        auto old_cfg = config_.load(std::memory_order_relaxed);
        std::shared_ptr<const AppConfig> new_cfg;

        do {
            // Створення нового об'єкта на основі зчитаних даних
            new_cfg = std::make_shared<const AppConfig>(
                old_cfg->host, 
                new_port, 
                old_cfg->max_connections
            );
        } while (!config_.compare_exchange_weak(
            old_cfg, 
            new_cfg,
            std::memory_order_release,
            std::memory_order_relaxed
        ));
        // Завдяки std::shared_ptr старий об'єкт буде автоматично знищено 
        // лише тоді, коли останній потік-читач завершить роботу з ним.
    }
};
