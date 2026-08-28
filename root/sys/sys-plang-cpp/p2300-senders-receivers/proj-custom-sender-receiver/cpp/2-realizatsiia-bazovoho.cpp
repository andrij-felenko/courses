#include <iostream>
#include <chrono>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <queue>
#include <functional>
#include <atomic>
#include <optional>
#include <utility>
#include <exception>
#include <concepts>

// Фоновий сервіс черги таймерів без блокування робочих потоків
class timer_service {
public:
    struct timer_entry {
        std::chrono::steady_clock::time_point deadline;
        std::function<void(bool cancelled)> callback;
        uint64_t id;

        // Пріоритетна черга впорядковує за найменшим дедлайном
        bool operator>(const timer_entry& other) const noexcept {
            return deadline > other.deadline;
        }
    };

    timer_service() : running_(true), next_id_(1), worker_(&timer_service::loop, this) {}

    ~timer_service() {
        {
            std::lock_guard<std::mutex> lock(mtx_);
            running_ = false;
        }
        cv_.notify_all();
        if (worker_.joinable()) {
            worker_.join();
        }
    }

    // Реєстрація нового таймера; повертає унікальний ідентифікатор
    uint64_t schedule_after(std::chrono::milliseconds duration, std::function<void(bool)> cb) {
        auto deadline = std::chrono::steady_clock::now() + duration;
        uint64_t timer_id = 0;
        {
            std::lock_guard<std::mutex> lock(mtx_);
            timer_id = next_id_++;
            timers_.push({deadline, std::move(cb), timer_id});
        }
        cv_.notify_all();
        return timer_id;
    }

private:
    void loop() {
        std::unique_lock<std::mutex> lock(mtx_);
        while (running_) {
            if (timers_.empty()) {
                // Черга порожня: чекаємо на появу нових таймерів або зупинку сервісу
                cv_.wait(lock, [this] { return !running_ || !timers_.empty(); });
            } else {
                auto now = std::chrono::steady_clock::now();
                auto top = timers_.top();
                if (now >= top.deadline) {
                    // Час таймера настав: вилучаємо з черги та виконуємо зворотний виклик без утримання замка
                    timers_.pop();
                    lock.unlock();
                    top.callback(false); // false = успішне спрацювання без скасування
                    lock.lock();
                } else {
                    // Спимо рівно до дедлайну найближчого таймера
                    cv_.wait_until(lock, top.deadline, [this, &top] {
                        return !running_ || timers_.empty() || timers_.top().deadline < top.deadline;
                    });
                }
            }
        }
    }

    std::mutex mtx_;
    std::condition_variable cv_;
    std::priority_queue<timer_entry, std::vector<timer_entry>, std::greater<>> timers_;
    std::atomic<bool> running_;
    uint64_t next_id_;
    std::thread worker_;
};
