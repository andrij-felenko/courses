#include <atomic>
#include <chrono>
#include <cstdint>
#include <expected>
#include <functional>
#include <span>
#include <string_view>

namespace resilience {

enum class State : uint8_t {
    Closed = 0,
    Open = 1,
    HalfOpen = 2
};

struct Config {
    uint32_t failure_rate_threshold{50};
    uint32_t minimum_number_of_calls{20};
    std::chrono::nanoseconds wait_duration_in_open{std::chrono::seconds(5)};
    uint32_t permitted_half_open_calls{10};
};

class CircuitBreaker {
public:
    static constexpr size_t WindowSize = 64;
    static constexpr size_t WindowMask = WindowSize - 1;

    explicit CircuitBreaker(Config config)
        : config_(config),
          state_(State::Closed),
          head_index_(0),
          last_state_change_(std::chrono::steady_clock::now()),
          half_open_probe_count_(0),
          half_open_failure_count_(0) {
        for (auto& slot : ring_buffer_) {
            slot.store(false, std::memory_order_relaxed);
        }
    }

    [[nodiscard]] bool allow_request() noexcept {
        const State current = state_.load(std::memory_order_acquire);

        if (current == State::Closed) {
            return true;
        }

        if (current == State::Open) {
            const auto now = std::chrono::steady_clock::now();
            const auto last = last_state_change_.load(std::memory_order_acquire);
            if (now - last >= config_.wait_duration_in_open) {
                transition_to(State::Open, State::HalfOpen);
                return allow_request();
            }
            return false;
        }

        if (current == State::HalfOpen) {
            const uint32_t probe_id = half_open_probe_count_.fetch_add(1, std::memory_order_acq_rel);
            return probe_id < config_.permitted_half_open_calls;
        }

        return false;
    }

    void record_result(bool is_failure) noexcept {
        const State current = state_.load(std::memory_order_acquire);

        if (current == State::HalfOpen) {
            if (is_failure) {
                transition_to(State::HalfOpen, State::Open);
            } else {
                const uint32_t probes = half_open_probe_count_.load(std::memory_order_acquire);
                if (probes >= config_.permitted_half_open_calls) {
                    transition_to(State::HalfOpen, State::Closed);
                }
            }
            return;
        }

        if (current == State::Closed) {
            const uint64_t idx = head_index_.fetch_add(1, std::memory_order_acq_rel);
            ring_buffer_[idx & WindowMask].store(is_failure, std::memory_order_release);

            const uint64_t total = idx + 1;
            if (total >= config_.minimum_number_of_calls) {
                const size_t active_window = total < WindowSize ? static_cast<size_t>(total) : WindowSize;
                size_t failures = 0;
                for (size_t i = 0; i < active_window; ++i) {
                    if (ring_buffer_[i].load(std::memory_order_relaxed)) {
                        ++failures;
                    }
                }
                const uint32_t rate = static_cast<uint32_t>((failures * 100) / active_window);
                if (rate >= config_.failure_rate_threshold) {
                    transition_to(State::Closed, State::Open);
                }
            }
        }
    }

    template <typename Func, typename Fallback>
    auto execute(Func&& primary, Fallback&& fallback) 
        -> std::invoke_result_t<Func> {
        if (!allow_request()) {
            return fallback();
        }
        try {
            auto result = primary();
            record_result(false);
            return result;
        } catch (...) {
            record_result(true);
            return fallback();
        }
    }

    [[nodiscard]] State state() const noexcept {
        return state_.load(std::memory_order_acquire);
    }

private:
    void transition_to(State expected, State next) noexcept {
        if (state_.compare_exchange_strong(expected, next,
                                           std::memory_order_release,
                                           std::memory_order_relaxed)) {
            last_state_change_.store(std::chrono::steady_clock::now(), std::memory_order_release);
            if (next == State::HalfOpen) {
                half_open_probe_count_.store(0, std::memory_order_release);
                half_open_failure_count_.store(0, std::memory_order_release);
            } else if (next == State::Closed) {
                head_index_.store(0, std::memory_order_release);
                for (auto& slot : ring_buffer_) {
                    slot.store(false, std::memory_order_relaxed);
                }
            }
        }
    }

    const Config config_;
    alignas(64) std::atomic<State> state_;
    alignas(64) std::atomic<uint64_t> head_index_;
    alignas(64) std::array<std::atomic<bool>, WindowSize> ring_buffer_;
    alignas(64) std::atomic<std::chrono::steady_clock::time_point> last_state_change_;
    alignas(64) std::atomic<uint32_t> half_open_probe_count_;
    alignas(64) std::atomic<uint32_t> half_open_failure_count_;
};

} // namespace resilience
