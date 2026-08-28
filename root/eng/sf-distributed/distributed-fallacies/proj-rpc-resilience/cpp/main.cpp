#include <iostream>
#include <string>
#include <string_view>
#include <chrono>
#include <random>
#include <optional>
#include <expected>
#include <thread>
#include <format>

enum class CircuitState {
    Closed,
    Open,
    HalfOpen
};

struct RpcPolicy {
    std::chrono::milliseconds timeout{2000};
    uint32_t max_retries{4};
    std::chrono::milliseconds base_backoff{50};
    std::chrono::milliseconds max_backoff{800};
};

struct RpcRequest {
    std::string idempotency_key;
    std::string payload;
};

struct RpcResponse {
    int status_code{200};
    std::string body;
};

enum class RpcError {
    Timeout,
    CircuitOpen,
    ServerError,
    ClientError
};

class CircuitBreaker {
public:
    CircuitBreaker(uint32_t failure_threshold, std::chrono::milliseconds cooloff)
        : threshold_(failure_threshold), cooloff_(cooloff) {}

    bool allow_request() {
        auto now = std::chrono::steady_clock::now();
        if (state_ == CircuitState::Open) {
            if (now - last_state_change_ >= cooloff_) {
                state_ = CircuitState::HalfOpen;
                return true;
            }
            return false;
        }
        return true;
    }

    void record_result(bool is_success) {
        auto now = std::chrono::steady_clock::now();
        if (is_success) {
            failure_count_ = 0;
            state_ = CircuitState::Closed;
        } else {
            failure_count_++;
            if (state_ == CircuitState::HalfOpen || failure_count_ >= threshold_) {
                state_ = CircuitState::Open;
                last_state_change_ = now;
            }
        }
    }

    CircuitState state() const { return state_; }

private:
    CircuitState state_{CircuitState::Closed};
    uint32_t failure_count_{0};
    uint32_t threshold_{3};
    std::chrono::milliseconds cooloff_{5000};
    std::chrono::steady_clock::time_point last_state_change_{std::chrono::steady_clock::now()};
};

class ResilientRpcClient {
public:
    explicit ResilientRpcClient(CircuitBreaker& cb, std::mt19937& rng)
        : cb_(cb), rng_(rng) {}

    std::expected<RpcResponse, RpcError> invoke(const RpcRequest& req, const RpcPolicy& policy) {
        const auto start = std::chrono::steady_clock::now();
        const auto deadline = start + policy.timeout;

        for (uint32_t attempt = 0; attempt < policy.max_retries; ++attempt) {
            if (std::chrono::steady_clock::now() >= deadline) {
                return std::unexpected(RpcError::Timeout);
            }

            if (!cb_.allow_request()) {
                return std::unexpected(RpcError::CircuitOpen);
            }

            auto result = mock_network_io(req);
            cb_.record_result(result.has_value());

            if (result.has_value()) {
                return result.value();
            }

            if (result.error() == RpcError::ClientError) {
                return std::unexpected(RpcError::ClientError);
            }

            auto backoff = compute_full_jitter(policy.base_backoff, policy.max_backoff, attempt);
            if (std::chrono::steady_clock::now() + backoff >= deadline) {
                return std::unexpected(RpcError::Timeout);
            }

            std::this_thread::sleep_for(backoff);
        }

        return std::unexpected(RpcError::ServerError);
    }

private:
    std::chrono::milliseconds compute_full_jitter(
        std::chrono::milliseconds base,
        std::chrono::milliseconds max_val,
        uint32_t attempt)
    {
        uint64_t multiplier = 1ULL << std::min(attempt, 20U);
        auto limit_ms = std::min(max_val.count(), base.count() * multiplier);
        std::uniform_int_distribution<uint64_t> dist(0, limit_ms);
        return std::chrono::milliseconds(dist(rng_));
    }

    std::expected<RpcResponse, RpcError> mock_network_io(const RpcRequest& req) {
        std::uniform_int_distribution<int> dist(0, 99);
        if (dist(rng_) < 40) {
            return std::unexpected(RpcError::ServerError);
        }
        return RpcResponse{
            .status_code = 200,
            .body = "Transaction completed for: " + req.idempotency_key
        };
    }

    CircuitBreaker& cb_;
    std::mt19937& rng_;
};
