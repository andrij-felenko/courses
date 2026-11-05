#include <atomic>
#include <mutex>
#include <memory>
#include <string>

// Стратегія 1: CAS з Copy-on-Write для конфігураційних об'єктів (Read-Heavy)
struct ServerConfig {
    std::string endpoint;
    int max_connections;
};

class CowConfigManager {
private:
    std::atomic<ServerConfig*> active_config_{new ServerConfig{"127.0.0.1", 8080}};

public:
    void update_config(std::string new_endpoint, int new_max_conn) {
        auto* new_cfg = new ServerConfig{std::move(new_endpoint), new_max_conn};
        ServerConfig* expected = active_config_.load(std::memory_order_relaxed);

        while (!active_config_.compare_exchange_weak(
            expected, new_cfg,
            std::memory_order_release,
            std::memory_order_relaxed)) {}
    }

    ServerConfig get_config() const {
        // Читач отримує актуальний вказівник без жодного блокування
        ServerConfig* cfg = active_config_.load(std::memory_order_acquire);
        return *cfg;
    }
};

// Стратегія 2: Традиційний Mutex для частіших модифікацій складеного стану
class MutexStateManager {
private:
    mutable std::mutex mutex_;
    ServerConfig state_{"127.0.0.1", 8080};

public:
    void update_fields(std::string endpoint, int max_conn) {
        std::lock_guard<std::mutex> lock(mutex_);
        state_.endpoint = std::move(endpoint);
        state_.max_connections = max_conn;
    }
};
