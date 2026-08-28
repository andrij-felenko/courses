// C++ Implementation: Idiomatic Adaptive Load Shedder and Circuit Breaker (RAII, Concurrency)
#include <iostream>
#include <atomic>
#include <chrono>
#include <memory>
#include <optional>
#include <expected>
#include <string>

enum class CircuitState {
    Closed,
    Open,
    HalfOpen
};

class ResilienceGuard {
public:
    ResilienceGuard(int max_concurrency, int failure_threshold, std::chrono::milliseconds cooldown)
        : max_concurrency_(max_concurrency),
          failure_threshold_(failure_threshold),
          cooldown_(cooldown),
          state_(CircuitState::Closed),
          active_requests_(0),
          failure_count_(0),
          last_state_change_(std::chrono::steady_clock::now()) {}

    class Permit {
    public:
        Permit(ResilienceGuard& guard, bool allowed) : guard_(guard), allowed_(allowed), released_(false) {}
        ~Permit() {
            if (allowed_ && !released_) {
                guard_.release_permit(true);
            }
        }
        Permit(const Permit&) = delete;
        Permit& operator=(const Permit&) = delete;
        Permit(Permit&& other) noexcept : guard_(other.guard_), allowed_(other.allowed_), released_(other.released_) {
            other.released_ = true;
        }

        [[nodiscard]] bool is_allowed() const noexcept { return allowed_; }
        void complete(bool success) {
            if (allowed_ && !released_) {
                released_ = true;
                guard_.release_permit(success);
            }
        }

    private:
        ResilienceGuard& guard_;
        bool allowed_;
        bool released_;
    };

    [[nodiscard]] Permit acquire_permit() {
        auto now = std::chrono::steady_clock::now();
        CircuitState current = state_.load(std::memory_order_relaxed);

        if (current == CircuitState::Open) {
            if (now - last_state_change_.load(std::memory_order_relaxed) > cooldown_) {
                if (state_.compare_exchange_strong(current, CircuitState::HalfOpen)) {
                    last_state_change_.store(now, std::memory_order_relaxed);
                    current = CircuitState::HalfOpen;
                }
            } else {
                return Permit(*this, false); // Rejected by Circuit Breaker
            }
        }

        if (active_requests_.load(std::memory_order_relaxed) >= max_concurrency_) {
            return Permit(*this, false); // Load Shedding: Concurrency limit hit
        }

        active_requests_.fetch_add(1, std::memory_order_relaxed);
        return Permit(*this, true);
    }

private:
    void release_permit(bool success) {
        active_requests_.fetch_sub(1, std::memory_order_relaxed);
        auto now = std::chrono::steady_clock::now();
        CircuitState current = state_.load(std::memory_order_relaxed);

        if (success) {
            if (current == CircuitState::HalfOpen) {
                state_.store(CircuitState::Closed, std::memory_order_relaxed);
                failure_count_.store(0, std::memory_order_relaxed);
                last_state_change_.store(now, std::memory_order_relaxed);
            } else if (current == CircuitState::Closed) {
                failure_count_.store(0, std::memory_order_relaxed);
            }
        } else {
            int failures = failure_count_.fetch_add(1, std::memory_order_relaxed) + 1;
            if (failures >= failure_threshold_ && current != CircuitState::Open) {
                state_.store(CircuitState::Open, std::memory_order_relaxed);
                last_state_change_.store(now, std::memory_order_relaxed);
            }
        }
    }

    const int max_concurrency_;
    const int failure_threshold_;
    const std::chrono::milliseconds cooldown_;

    std::atomic<CircuitState> state_;
    std::atomic<int> active_requests_;
    std::atomic<int> failure_count_;
    std::atomic<std::chrono::steady_clock::time_point> last_state_change_;
};
