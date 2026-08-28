#include <iostream>
#include <memory>
#include <random>
#include <thread>
#include <chrono>
#include <atomic>
#include <expected>
#include <string_view>

struct ChaosConfig {
    std::atomic<int32_t> latency_ms{0};
    std::atomic<int32_t> error_rate_percent{0};
    std::atomic<bool> is_ready{true};
};

class ChaosInterceptor {
public:
    explicit ChaosInterceptor(std::shared_ptr<ChaosConfig> config)
        : config_(std::move(config)), rng_(std::random_device{}()) {}

    [[nodiscard]] std::expected<std::string_view, int>
    process_request(std::string_view target_header, std::string_view payload) {
        if (target_header == "twin-cache") {
            const int lat = config_->latency_ms.load(std::memory_order_relaxed);
            if (lat > 0) {
                std::this_thread::sleep_for(std::chrono::milliseconds(lat));
            }

            const int err_rate = config_->error_rate_percent.load(std::memory_order_relaxed);
            if (err_rate > 0) {
                std::uniform_int_distribution<int> dist(0, 99);
                if (dist(rng_) < err_rate) {
                    return std::unexpected(500); // Simulated 500 Internal Error
                }
            }
        }
        return payload;
    }

    [[nodiscard]] bool check_liveness() const noexcept {
        // Liveness перевіряє лише те, що потік не заблокований навічно
        return true;
    }

    [[nodiscard]] bool check_readiness() const noexcept {
        // Readiness повертає false, коли кеш впав, знімаючи трафік з балансувальника
        return config_->is_ready.load(std::memory_order_relaxed);
    }

private:
    std::shared_ptr<ChaosConfig> config_;
    mutable std::mt19937 rng_;
};
