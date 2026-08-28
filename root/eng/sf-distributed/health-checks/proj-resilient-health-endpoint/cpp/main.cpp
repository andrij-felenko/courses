#include <iostream>
#include <string>
#include <string_view>
#include <chrono>
#include <mutex>
#include <atomic>
#include <format>
#include <cstdint>

enum class HealthStatus {
    Healthy,
    Degraded,
    Unhealthy
};

struct HealthReport {
    HealthStatus status{HealthStatus::Healthy};
    int http_code{200};
    std::chrono::steady_clock::time_point evaluated_at{};
    std::string details{};
};

class ResilientHealthMonitor {
public:
    explicit ResilientHealthMonitor(size_t memory_limit_mb, int max_workers)
        : memory_limit_mb_(memory_limit_mb), max_workers_(max_workers) {}

    // Ініціація граційного зняття трафіку під час отримання SIGTERM
    void trigger_drain() noexcept {
        is_draining_.store(true, std::memory_order_release);
        std::lock_guard<std::mutex> lock(mutex_);
        cached_readiness_.evaluated_at = std::chrono::steady_clock::time_point{};
    }

    void update_system_metrics(size_t mem_used_mb, int active_workers, 
                               bool db_ok, int db_conns) {
        std::lock_guard<std::mutex> lock(mutex_);
        memory_used_mb_ = mem_used_mb;
        active_workers_ = active_workers;
        db_pool_connected_ = db_ok;
        available_db_conns_ = db_conns;
    }

    // 1. Liveness: швидка перевірка внутрішнього стану процесу в пам'яті
    [[nodiscard]] HealthReport check_liveness() {
        const auto now = std::chrono::steady_clock::now();
        std::lock_guard<std::mutex> lock(mutex_);

        // Перевірка TTL кешу
        if (cached_liveness_.evaluated_at.time_since_epoch().count() > 0 &&
            (now - cached_liveness_.evaluated_at) < kCacheTtl) {
            return cached_liveness_;
        }

        HealthReport report;
        report.evaluated_at = now;

        if (memory_used_mb_ > memory_limit_mb_) {
            report.status = HealthStatus::Unhealthy;
            report.http_code = 500;
            report.details = "CRITICAL: Heap allocation exceeded limit";
        } else {
            report.status = HealthStatus::Healthy;
            report.http_code = 200;
            report.details = "OK: Process internal event loop healthy";
        }

        cached_liveness_ = report;
        return report;
    }

    // 2. Readiness: оцінка здатності приймати трафік користувачів
    [[nodiscard]] HealthReport check_readiness() {
        const auto now = std::chrono::steady_clock::now();
        std::lock_guard<std::mutex> lock(mutex_);

        if (cached_readiness_.evaluated_at.time_since_epoch().count() > 0 &&
            (now - cached_readiness_.evaluated_at) < kCacheTtl) {
            return cached_readiness_;
        }

        HealthReport report;
        report.evaluated_at = now;

        if (is_draining_.load(std::memory_order_acquire)) {
            report.status = HealthStatus::Unhealthy;
            report.http_code = 503;
            report.details = "SHUTDOWN: Instance is draining traffic";
            cached_readiness_ = report;
            return report;
        }

        const bool is_ready_now = (db_pool_connected_ && available_db_conns_ > 0);

        // Фільтрація миготіння (Hysteresis)
        if (!is_ready_now) {
            ++consecutive_failures_;
            consecutive_successes_ = 0;
            if (consecutive_failures_ >= kFailureThreshold) {
                current_readiness_ = HealthStatus::Unhealthy;
            }
        } else {
            ++consecutive_successes_;
            consecutive_failures_ = 0;
            if (consecutive_successes_ >= kSuccessThreshold) {
                current_readiness_ = HealthStatus::Healthy;
            }
        }

        if (current_readiness_ == HealthStatus::Healthy) {
            report.status = HealthStatus::Healthy;
            report.http_code = 200;
            report.details = "OK: Ready to serve traffic";
        } else {
            report.status = HealthStatus::Unhealthy;
            report.http_code = 503;
            report.details = "UNAVAILABLE: Resources exhausted or degraded";
        }

        cached_readiness_ = report;
        return report;
    }

private:
    static constexpr std::chrono::milliseconds kCacheTtl{2000};
    static constexpr int kFailureThreshold = 3;
    static constexpr int kSuccessThreshold = 2;

    std::mutex mutex_;
    size_t memory_used_mb_{64};
    size_t memory_limit_mb_{512};
    int active_workers_{2};
    int max_workers_{16};
    
    bool db_pool_connected_{true};
    int available_db_conns_{10};
    std::atomic<bool> is_draining_{false};

    int consecutive_failures_{0};
    int consecutive_successes_{kSuccessThreshold};
    HealthStatus current_readiness_{HealthStatus::Healthy};

    HealthReport cached_liveness_{};
    HealthReport cached_readiness_{};
};

int main() {
    ResilientHealthMonitor monitor(512, 16);

    std::cout << "=== C++20 Resilient Health Check Engine ===\n\n";

    auto liveness = monitor.check_liveness();
    auto readiness = monitor.check_readiness();

    std::cout << "[1] Liveness:  HTTP " << liveness.http_code << " (" << liveness.details << ")\n";
    std::cout << "    Readiness: HTTP " << readiness.http_code << " (" << readiness.details << ")\n\n";

    // Активація фази Drain
    monitor.trigger_drain();
    auto liveness_drain = monitor.check_liveness();
    auto readiness_drain = monitor.check_readiness();

    std::cout << "[2] Під час зупинки сервісу:\n";
    std::cout << "    Readiness: HTTP " << readiness_drain.http_code << " -> Балансувальник вилучає вузол\n";
    std::cout << "    Liveness:  HTTP " << liveness_drain.http_code  << " -> Оркестратор НЕ вбиває под до завершення з'єднань\n";

    return 0;
}
