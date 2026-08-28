#include <iostream>
#include <chrono>
#include <mutex>
#include <condition_variable>
#include <atomic>
#include <optional>
#include <functional>
#include <expected>
#include <string_view>

namespace resilience {

enum class BulkheadError {
    CapacityExceeded,
    TimeoutWaitingForSlot,
    CircuitBroken
};

class Bulkhead {
public:
    struct Metrics {
        std::size_t available_permits;
        std::size_t max_permits;
        uint64_t total_acquired;
        uint64_t total_rejected;
    };

    class PermitGuard {
    public:
        PermitGuard(Bulkhead& parent) noexcept : parent_(&parent) {}
        
        ~PermitGuard() noexcept {
            if (parent_ != nullptr) {
                parent_->release();
            }
        }

        PermitGuard(const PermitGuard&) = delete;
        PermitGuard& operator=(const PermitGuard&) = delete;

        PermitGuard(PermitGuard&& other) noexcept : parent_(other.parent_) {
            other.parent_ = nullptr;
        }

        PermitGuard& operator=(PermitGuard&& other) noexcept {
            if (this != &other) {
                if (parent_ != nullptr) {
                    parent_->release();
                }
                parent_ = other.parent_;
                other.parent_ = nullptr;
            }
            return *this;
        }

    private:
        Bulkhead* parent_{nullptr};
    };

    Bulkhead(std::string_view name, std::size_t max_concurrent_calls, 
             std::chrono::milliseconds max_wait_duration = std::chrono::milliseconds(0))
        : name_(name),
          max_permits_(max_concurrent_calls),
          available_permits_(max_concurrent_calls),
          max_wait_duration_(max_wait_duration),
          total_acquired_(0),
          total_rejected_(0) {}

    ~Bulkhead() = default;

    std::expected<PermitGuard, BulkheadError> try_acquire() {
        if (max_wait_duration_.count() == 0) {
            // Швидка спроба без очікування
            std::unique_lock<std::mutex> lock(mutex_);
            if (available_permits_ > 0) {
                --available_permits_;
                total_acquired_.fetch_add(1, std::memory_order_relaxed);
                return PermitGuard(*this);
            }
            total_rejected_.fetch_add(1, std::memory_order_relaxed);
            return std::unexpected(BulkheadError::CapacityExceeded);
        }

        // Спроба з очікуванням у межах бюджету часу
        std::unique_lock<std::mutex> lock(mutex_);
        if (available_permits_ == 0) {
            auto status = cv_.wait_for(lock, max_wait_duration_, [this]() {
                return available_permits_ > 0;
            });
            if (!status) {
                total_rejected_.fetch_add(1, std::memory_order_relaxed);
                return std::unexpected(BulkheadError::TimeoutWaitingForSlot);
            }
        }

        --available_permits_;
        total_acquired_.fetch_add(1, std::memory_order_relaxed);
        return PermitGuard(*this);
    }

    template <typename Func, typename Fallback>
    auto execute(Func&& action, Fallback&& fallback) 
        -> std::invoke_result_t<Func> {
        auto permit = try_acquire();
        if (permit.has_value()) {
            return std::forward<Func>(action)();
        }
        return std::forward<Fallback>(fallback)(permit.error());
    }

    Metrics get_metrics() const noexcept {
        std::unique_lock<std::mutex> lock(mutex_);
        return Metrics{
            available_permits_,
            max_permits_,
            total_acquired_.load(std::memory_order_relaxed),
            total_rejected_.load(std::memory_order_relaxed)
        };
    }

private:
    void release() noexcept {
        {
            std::unique_lock<std::mutex> lock(mutex_);
            if (available_permits_ < max_permits_) {
                ++available_permits_;
            }
        }
        cv_.notify_one();
    }

    std::string name_;
    const std::size_t max_permits_;
    std::size_t available_permits_;
    const std::chrono::milliseconds max_wait_duration_;
    mutable std::mutex mutex_;
    std::condition_variable cv_;
    std::atomic<uint64_t> total_acquired_;
    std::atomic<uint64_t> total_rejected_;
};

} // namespace resilience
