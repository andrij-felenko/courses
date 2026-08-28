#include <iostream>
#include <atomic>
#include <chrono>
#include <mutex>
#include <algorithm>
#include <cmath>
#include <optional>

enum class RequestPriority {
    Low    = 0,
    Normal = 1,
    High   = 2
};

class AdaptiveAdmissionController {
public:
    struct Config {
        int min_limit = 10;
        int max_limit = 500;
        double smoothing_factor = 0.1;
        double headroom = 1.0;
    };

    explicit AdaptiveAdmissionController(Config config)
        : config_(config),
          limit_(config.min_limit),
          in_flight_(0),
          min_rtt_(std::chrono::duration<double, std::milli>::zero()),
          smoothed_rtt_(std::chrono::duration<double, std::milli>::zero()) {}

    class Permit {
    public:
        Permit(AdaptiveAdmissionController& parent, std::chrono::steady_clock::time_point start)
            : parent_(&parent), start_time_(start) {}
        
        ~Permit() {
            if (parent_) {
                auto duration = std::chrono::duration<double, std::milli>(
                    std::chrono::steady_clock::now() - start_time_
                );
                parent_->release(duration.count());
            }
        }
        
        Permit(const Permit&) = delete;
        Permit& operator=(const Permit&) = delete;
        
        Permit(Permit&& other) noexcept 
            : parent_(other.parent_), start_time_(other.start_time_) {
            other.parent_ = nullptr;
        }

        Permit& operator=(Permit&& other) noexcept {
            if (this != &other) {
                if (parent_) {
                    auto duration = std::chrono::duration<double, std::milli>(
                        std::chrono::steady_clock::now() - start_time_
                    );
                    parent_->release(duration.count());
                }
                parent_ = other.parent_;
                start_time_ = other.start_time_;
                other.parent_ = nullptr;
            }
            return *this;
        }

    private:
        AdaptiveAdmissionController* parent_;
        std::chrono::steady_clock::time_point start_time_;
    };

    [[nodiscard]] std::optional<Permit> try_acquire(
        RequestPriority prio, 
        std::optional<std::chrono::steady_clock::time_point> deadline = std::nullopt) 
    {
        const auto now = std::chrono::steady_clock::now();
        
        // 1. Перевірка дедлайну
        if (deadline && now >= *deadline) {
            return std::nullopt;
        }

        const int cur_limit = limit_.load(std::memory_order_relaxed);
        int cur_in_flight = in_flight_.load(std::memory_order_relaxed);

        // 2. Пріоритетне скидання навантаження
        if (prio == RequestPriority::Low && cur_in_flight >= static_cast<int>(cur_limit * 0.80)) {
            return std::nullopt;
        }
        if (prio == RequestPriority::Normal && cur_in_flight >= static_cast<int>(cur_limit * 0.95)) {
            return std::nullopt;
        }

        // 3. Атомарне захоплення слота (Lock-free CAS)
        while (cur_in_flight < cur_limit) {
            if (in_flight_.compare_exchange_weak(cur_in_flight, cur_in_flight + 1,
                                                 std::memory_order_acquire,
                                                 std::memory_order_relaxed)) {
                return Permit(*this, now);
            }
        }

        return std::nullopt;
    }

    [[nodiscard]] int current_limit() const noexcept {
        return limit_.load(std::memory_order_relaxed);
    }

    [[nodiscard]] int active_in_flight() const noexcept {
        return in_flight_.load(std::memory_order_relaxed);
    }

private:
    void release(double duration_ms) {
        in_flight_.fetch_sub(1, std::memory_order_release);

        std::lock_guard<std::mutex> lock(metrics_mutex_);

        // Оновлення мінімального базового часу відгуку
        if (min_rtt_.count() <= 0.0 || duration_ms < min_rtt_.count()) {
            min_rtt_ = std::chrono::duration<double, std::milli>(duration_ms);
        }

        // Експоненційне згладжування затримки (EWMA)
        if (smoothed_rtt_.count() <= 0.0) {
            smoothed_rtt_ = std::chrono::duration<double, std::milli>(duration_ms);
        } else {
            smoothed_rtt_ = std::chrono::duration<double, std::milli>(
                (1.0 - config_.smoothing_factor) * smoothed_rtt_.count() +
                config_.smoothing_factor * duration_ms
            );
        }

        // Розрахунок градієнта та оновлення ліміту
        if (min_rtt_.count() > 0.0 && smoothed_rtt_.count() > 0.0) {
            double gradient = min_rtt_.count() / smoothed_rtt_.count();
            gradient = std::min(gradient, 1.0);

            const int cur_limit = limit_.load(std::memory_order_relaxed);
            const double new_limit = static_cast<double>(cur_limit) * gradient + config_.headroom;

            int target = static_cast<int>(std::round(new_limit));
            target = std::clamp(target, config_.min_limit, config_.max_limit);

            limit_.store(target, std::memory_order_relaxed);
        }
    }

    Config config_;
    std::atomic<int> limit_;
    std::atomic<int> in_flight_;
    
    std::mutex metrics_mutex_;
    std::chrono::duration<double, std::milli> min_rtt_;
    std::chrono::duration<double, std::milli> smoothed_rtt_;
};
