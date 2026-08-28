#include <iostream>
#include <string>
#include <string_view>
#include <chrono>
#include <random>
#include <thread>
#include <expected>
#include <format>
#include <algorithm>

struct HttpResponsePayload {
    int status_code{0};
    int retry_after_sec{0};
    std::string response_body;
};

enum class ClientFailure {
    FatalStatus,
    TransientLimitReached
};

class ResilientHttpClientWrapper {
public:
    struct Options {
        int max_attempts = 3;
        std::chrono::milliseconds base_delay{100};
        std::chrono::milliseconds max_delay{10000};
    };

    explicit ResilientHttpClientWrapper(Options opt = {})
        : opt_(opt), rng_(std::random_device{}()) {}

    std::expected<HttpResponsePayload, ClientFailure> post(std::string_view url, std::string_view body) {
        const std::string idempotency_key = create_uuid_v4();

        for (int attempt = 0; attempt <= opt_.max_attempts; ++attempt) {
            HttpResponsePayload resp = mock_transport_send("POST", url, idempotency_key, body, attempt);

            if (resp.status_code >= 200 && resp.status_code < 300) {
                return resp;
            }

            const bool is_transient = (resp.status_code == 429 ||
                                       resp.status_code == 502 ||
                                       resp.status_code == 503 ||
                                       resp.status_code == 504);

            if (!is_transient || attempt == opt_.max_attempts) {
                return std::unexpected(ClientFailure::TransientLimitReached);
            }

            const auto pause = compute_full_jitter_delay(attempt, resp.retry_after_sec);
            std::this_thread::sleep_for(pause);
        }

        return std::unexpected(ClientFailure::TransientLimitReached);
    }

private:
    Options opt_;
    std::mt19937 rng_;

    std::chrono::milliseconds compute_full_jitter_delay(int attempt, int retry_after_sec) {
        if (retry_after_sec > 0) {
            std::uniform_int_distribution<int> jitter(0, 150);
            return std::chrono::seconds(retry_after_sec) + std::chrono::milliseconds(jitter(rng_));
        }

        const auto exponential_limit = opt_.base_delay.count() * (1LL << attempt);
        const auto capped_limit = std::min(static_cast<long long>(opt_.max_delay.count()), exponential_limit);

        std::uniform_int_distribution<long long> dist(0, capped_limit);
        return std::chrono::milliseconds(dist(rng_));
    }

    std::string create_uuid_v4() {
        std::uniform_int_distribution<uint32_t> dist(0, 0xFFFFFFFF);
        return std::format("{:08x}-{:04x}-4{:03x}-a{:03x}-{:08x}",
                           dist(rng_), dist(rng_) & 0xFFFF,
                           dist(rng_) & 0x0FFF, dist(rng_) & 0x0FFF, dist(rng_));
    }

    HttpResponsePayload mock_transport_send(std::string_view method, std::string_view url,
                                            std::string_view idemp_key, std::string_view body, int attempt) {
        if (attempt < 2) {
            return HttpResponsePayload{.status_code = 503, .retry_after_sec = 0, .response_body = "Unavailable"};
        }
        return HttpResponsePayload{
            .status_code = 201,
            .retry_after_sec = 0,
            .response_body = std::format(R"({{"status":"Created","idempotency_key":"{}"}})", idemp_key)
        };
    }
};
