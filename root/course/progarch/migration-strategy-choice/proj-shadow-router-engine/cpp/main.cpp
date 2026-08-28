// cpp
#include <iostream>
#include <string>
#include <string_view>
#include <memory>
#include <functional>
#include <thread>
#include <mutex>
#include <atomic>
#include <chrono>
#include <expected>

struct Request {
    std::string request_id;
    std::string payload;
    int user_id;
};

struct Response {
    int status_code{200};
    std::string data;
    double latency_ms{0.0};

    bool operator==(const Response& other) const {
        return status_code == other.status_code && data == other.data;
    }
};

enum class MigrationError {
    Timeout,
    InternalError,
    ServiceUnavailable
};

using ServiceHandler = std::function<std::expected<Response, MigrationError>(const Request&)>;

class ShadowRouter {
public:
    ShadowRouter(ServiceHandler primary, ServiceHandler shadow, bool enable_parallel_run)
        : primary_service_(std::move(primary)),
          shadow_service_(std::move(shadow)),
          enable_parallel_run_(enable_parallel_run) {}

    ~ShadowRouter() = default;

    std::expected<Response, MigrationError> dispatch(const Request& req) {
        // 1. Синхронний виклик первинної системи (повертається клієнту)
        auto start = std::chrono::high_resolution_clock::now();
        auto primary_res = primary_service_(req);
        auto end = std::chrono::high_resolution_clock::now();

        if (!primary_res.has_value()) {
            return primary_res;
        }

        // 2. Асинхронний тіньовий прогон (Dark Launch / Dual Run)
        std::jthread([this, req, primary_resp = primary_res.value()]() {
            auto shadow_res = shadow_service_(req);
            total_processed_++;

            if (enable_parallel_run_ && shadow_res.has_value()) {
                if (primary_resp != shadow_res.value()) {
                    diff_count_++;
                    std::lock_guard<std::mutex> lock(log_mutex_);
                    std::cerr << "[RECONCILER ALERT] ID: " << req.request_id
                              << " | Primary: '" << primary_resp.data
                              << "' | Shadow: '" << shadow_res.value().data << "'\n";
                }
            } else if (!shadow_res.has_value()) {
                diff_count_++;
            }
        }).detach();

        return primary_res;
    }

    uint64_t total_processed() const { return total_processed_.load(); }
    uint64_t diff_count() const { return diff_count_.load(); }

private:
    ServiceHandler primary_service_;
    ServiceHandler shadow_service_;
    bool enable_parallel_run_;

    std::atomic<uint64_t> total_processed_{0};
    std::atomic<uint64_t> diff_count_{0};
    std::mutex log_mutex_;
};
