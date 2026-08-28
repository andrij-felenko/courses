#include <iostream>
#include <string>
#include <string_view>
#include <chrono>
#include <random>
#include <memory>
#include <unordered_map>
#include <expected>
#include <optional>
#include <algorithm>

// ── 1. Типи даних та структури подій ───────────────────────────────────────
struct OutboxEvent {
    std::string id;
    std::string tenant_id;
    std::string destination_url;
    std::string secret_key;
    std::string event_type;
    std::string payload_json;
    int attempts = 0;
    int max_attempts = 10;
};

struct DeliveryResult {
    std::optional<int> status_code;
    std::chrono::milliseconds duration;
    std::string body;
    std::string error_message;
};

enum class DeliveryStatus {
    Delivered,
    RetryableFailed,
    DeadLetter
};

// ── 2. Алгоритм розрахунку Full Jitter ──────────────────────────────────────
class BackoffCalculator {
public:
    static std::chrono::milliseconds calculate_full_jitter(
        int attempt,
        std::chrono::milliseconds base_delay = std::chrono::milliseconds(1000),
        std::chrono::milliseconds max_delay = std::chrono::milliseconds(3600000)
    ) {
        int safe_shift = std::min(attempt, 30);
        uint64_t multiplier = 1ULL << safe_shift;
        uint64_t calculated = base_delay.count() * multiplier;
        uint64_t ceiling = std::min(static_cast<uint64_t>(max_delay.count()), calculated);

        static thread_local std::mt19937_64 rng(std::random_device{}());
        std::uniform_int_distribution<uint64_t> dist(0, ceiling);

        return std::chrono::milliseconds(dist(rng));
    }
};

// ── 3. Автомат станів Circuit Breaker ──────────────────────────────────────
enum class CircuitState { Closed, Open, HalfOpen };

class HostCircuitBreaker {
public:
    explicit HostCircuitBreaker(int threshold = 5, std::chrono::milliseconds cooldown = std::chrono::seconds(60))
        : failure_threshold_(threshold), cooldown_(cooldown),
          state_(CircuitState::Closed), consecutive_failures_(0),
          last_state_change_(std::chrono::steady_clock::now()) {}

    bool can_attempt() {
        auto now = std::chrono::steady_clock::now();
        if (state_ == CircuitState::Open) {
            if (now - last_state_change_ >= cooldown_) {
                state_ = CircuitState::HalfOpen;
                last_state_change_ = now;
                return true;
            }
            return false;
        }
        return true;
    }

    void record_success() {
        consecutive_failures_ = 0;
        state_ = CircuitState::Closed;
        last_state_change_ = std::chrono::steady_clock::now();
    }

    void record_failure() {
        consecutive_failures_++;
        if (state_ == CircuitState::HalfOpen || consecutive_failures_ >= failure_threshold_) {
            state_ = CircuitState::Open;
            last_state_change_ = std::chrono::steady_clock::now();
        }
    }

    CircuitState state() const { return state_; }

private:
    int failure_threshold_;
    std::chrono::milliseconds cooldown_;
    CircuitState state_;
    int consecutive_failures_;
    std::chrono::steady_clock::time_point last_state_change_;
};

// ── 4. Класифікатор наслідків доставки ──────────────────────────────────────
class OutcomeClassifier {
public:
    struct Decision {
        DeliveryStatus status;
        std::chrono::milliseconds next_retry_delay{0};
    };

    static Decision evaluate(const DeliveryResult& result, const OutboxEvent& event) {
        if (result.status_code.has_value() && *result.status_code >= 200 && *result.status_code < 300) {
            return Decision{DeliveryStatus::Delivered, std::chrono::milliseconds(0)};
        }

        bool is_permanent_4xx = result.status_code.has_value() &&
                                *result.status_code >= 400 && *result.status_code < 500 &&
                                *result.status_code != 408 && *result.status_code != 429;

        int next_attempt = event.attempts + 1;
        if (is_permanent_4xx || next_attempt >= event.max_attempts) {
            return Decision{DeliveryStatus::DeadLetter, std::chrono::milliseconds(0)};
        }

        auto delay = BackoffCalculator::calculate_full_jitter(next_attempt);
        return Decision{DeliveryStatus::RetryableFailed, delay};
    }
};
