#include <iostream>
#include <string>
#include <string_view>
#include <unordered_map>
#include <memory>
#include <chrono>
#include <random>
#include <cmath>
#include <functional>

enum class CircuitState { Closed, Open, HalfOpen };
enum class DeliveryResult { Sent, Retry, Dlq };

struct OutboundMessage {
    std::string id;
    std::string url;
    std::string payload;
    std::string secret;
    int attempt{0};
    int maxAttempts{5};
};

class CircuitBreaker {
public:
    explicit CircuitBreaker(int threshold = 3, std::chrono::seconds resetTimeout = std::chrono::seconds(10))
        : threshold_(threshold), resetTimeout_(resetTimeout) {}

    bool canExecute(std::chrono::steady_clock::time_point now) {
        if (state_ == CircuitState::Open) {
            if (now >= nextAttemptTime_) {
                state_ = CircuitState::HalfOpen;
                return true;
            }
            return false;
        }
        return true;
    }

    void onSuccess() {
        failureCount_ = 0;
        state_ = CircuitState::Closed;
    }

    void onFailure(std::chrono::steady_clock::time_point now) {
        failureCount_++;
        if (failureCount_ >= threshold_) {
            state_ = CircuitState::Open;
            nextAttemptTime_ = now + resetTimeout_;
        }
    }

    [[nodiscard]] CircuitState state() const noexcept { return state_; }

private:
    int threshold_;
    std::chrono::seconds resetTimeout_;
    CircuitState state_{CircuitState::Closed};
    int failureCount_{0};
    std::chrono::steady_clock::time_point nextAttemptTime_;
};

class EgressGateway {
public:
    using TransportFn = std::function<int(std::string_view url, std::string_view body, const std::unordered_map<std::string, std::string>& headers)>;

    explicit EgressGateway(CircuitBreaker cb = CircuitBreaker{}) : cb_(std::move(cb)) {}

    DeliveryResult processMessage(const OutboundMessage& msg, const TransportFn& transport) {
        auto now = std::chrono::steady_clock::now();
        if (!cb_.canExecute(now)) {
            return DeliveryResult::Retry;
        }

        std::unordered_map<std::string, std::string> headers{
            {"Content-Type", "application/json"},
            {"X-Idempotency-Key", msg.id}
        };

        try {
            int statusCode = transport(msg.url, msg.payload, headers);
            if (statusCode >= 200 && statusCode < 300) {
                cb_.onSuccess();
                return DeliveryResult::Sent;
            }
            if (statusCode >= 400 && statusCode < 500 && statusCode != 429) {
                return DeliveryResult::Dlq;
            }
            cb_.onFailure(std::chrono::steady_clock::now());
        } catch (...) {
            cb_.onFailure(std::chrono::steady_clock::now());
        }

        if (msg.attempt + 1 >= msg.maxAttempts) {
            return DeliveryResult::Dlq;
        }
        return DeliveryResult::Retry;
    }

    [[nodiscard]] std::chrono::milliseconds calculateBackoff(
        int attempt,
        std::chrono::milliseconds baseMs = std::chrono::milliseconds(100),
        std::chrono::milliseconds maxMs = std::chrono::milliseconds(5000)
    ) const {
        double temp = std::min(static_cast<double>(maxMs.count()), baseMs.count() * std::pow(2.0, attempt));
        std::uniform_real_distribution<double> dist(0.0, 0.5 * temp);
        thread_local std::mt19937 rng{std::random_device{}()};
        return std::chrono::milliseconds(static_cast<long long>(temp + dist(rng)));
    }

private:
    CircuitBreaker cb_;
};
