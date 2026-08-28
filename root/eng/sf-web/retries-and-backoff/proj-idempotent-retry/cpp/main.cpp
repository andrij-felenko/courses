#include <iostream>
#include <string>
#include <string_view>
#include <chrono>
#include <random>
#include <thread>
#include <expected>
#include <memory>
#include <format>
#include <atomic>

struct HttpResponse {
    int status_code{0};
    int retry_after_seconds{0};
    std::string body;
};

enum class HttpError {
    TransientNetworkFailure,
    CircuitOpen,
    RetryBudgetExhausted,
    FatalServerError,
    MaxRetriesExceeded
};

class ResilientHttpClientCpp {
public:
    struct Config {
        int max_retries = 3;
        std::chrono::milliseconds base_backoff{100};
        std::chrono::milliseconds max_backoff{10000};
    };

    explicit ResilientHttpClientCpp(Config cfg = {})
        : cfg_(cfg), rng_(std::random_device{}()) {}

    std::expected<HttpResponse, HttpError> execute_post(std::string_view url, std::string_view payload) {
        const std::string idempotency_key = generate_uuid_v4();

        for (int attempt = 0; attempt <= cfg_.max_retries; ++attempt) {
            HttpResponse res = mock_transport_call("POST", url, idempotency_key, payload, attempt);

            if (res.status_code >= 200 && res.status_code < 300) {
                return res;
            }

            const bool is_transient = (res.status_code == 429 ||
                                       res.status_code == 502 ||
                                       res.status_code == 503 ||
                                       res.status_code == 504);

            if (!is_transient || attempt == cfg_.max_retries) {
                return std::unexpected(HttpError::MaxRetriesExceeded);
            }

            const auto delay = compute_full_jitter(attempt, res.retry_after_seconds);
            std::this_thread::sleep_for(delay);
        }

        return std::unexpected(HttpError::MaxRetriesExceeded);
    }

private:
    Config cfg_;
    std::mt19937 rng_;

    std::chrono::milliseconds compute_full_jitter(int attempt, int retry_after_sec) {
        if (retry_after_sec > 0) {
            std::uniform_int_distribution<int> jitter_dist(0, 100);
            return std::chrono::seconds(retry_after_sec) + std::chrono::milliseconds(jitter_dist(rng_));
        }

        const auto exp_ms = cfg_.base_backoff.count() * (1LL << attempt);
        const auto capped_ms = std::min(static_cast<long long>(cfg_.max_backoff.count()), exp_ms);

        std::uniform_int_distribution<long long> dist(0, capped_ms);
        return std::chrono::milliseconds(dist(rng_));
    }

    std::string generate_uuid_v4() {
        std::uniform_int_distribution<uint32_t> dist(0, 0xFFFFFFFF);
        return std::format("idemp-{:08x}-{:04x}-4{:03x}-8{:03x}-{:08x}",
                           dist(rng_), dist(rng_) & 0xFFFF, dist(rng_) & 0x0FFF,
                           dist(rng_) & 0x0FFF, dist(rng_));
    }

    HttpResponse mock_transport_call(std::string_view method, std::string_view url,
                                     std::string_view key, std::string_view body, int attempt) {
        if (attempt < 2) {
            return HttpResponse{.status_code = 503, .retry_after_seconds = 0, .body = "Service Unavailable"};
        }
        return HttpResponse{.status_code = 200, .retry_after_seconds = 0,
                            .body = std::format(R"({{"status":"OK","idempotency_key":"{}"}})", key)};
    }
};
