#include <iostream>
#include <vector>
#include <string>
#include <queue>
#include <chrono>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <optional>
#include <atomic>
#include <expected>

namespace resilience {

using namespace std::chrono_literals;

enum class LevelerError {
    QueueFull,
    SystemShutdown
};

struct Task {
    uint64_t id{0};
    std::string payload;
    std::chrono::steady_clock::time_point enqueue_time;
    std::chrono::steady_clock::time_point deadline;
};

// Потокобезпечний маркерний кошик (Token Bucket)
class TokenBucket {
public:
    TokenBucket(double rate_rps, double capacity)
        : rate_per_sec_(rate_rps), capacity_(capacity), tokens_(capacity),
          last_refill_(std::chrono::steady_clock::now()) {}

    void consume() {
        while (true) {
            std::unique_lock lock(mutex_);
            auto now = std::chrono::steady_clock::now();
            std::chrono::duration<double> elapsed = now - last_refill_;
            tokens_ = std::min(capacity_, tokens_ + elapsed.count() * rate_per_sec_);
            last_refill_ = now;

            if (tokens_ >= 1.0) {
                tokens_ -= 1.0;
                return;
            }

            double missing = 1.0 - tokens_;
            auto wait_duration = std::chrono::duration_cast<std::chrono::microseconds>(
                std::chrono::duration<double>(missing / rate_per_sec_)
            );
            lock.unlock();

            std::this_thread::sleep_for(std::max(wait_duration, 500us));
        }
    }

private:
    std::mutex mutex_;
    const double rate_per_sec_;
    const double capacity_;
    double tokens_;
    std::chrono::steady_clock::time_point last_refill_;
};

// Демпфер навантаження чергою
class QueueLoadLeveler {
public:
    QueueLoadLeveler(size_t max_capacity, double max_rps)
        : max_capacity_(max_capacity), rate_limiter_(max_rps, max_rps * 0.2) {}

    ~QueueLoadLeveler() {
        stop();
    }

    // Асинхронна постановка задачі з миттєвим бекпреше при переповненні
    std::expected<uint64_t, LevelerError> enqueue(std::string payload, std::chrono::milliseconds ttl) {
        std::unique_lock lock(mutex_);

        if (shutdown_) {
            return std::unexpected(LevelerError::SystemShutdown);
        }

        if (queue_.size() >= max_capacity_) {
            rejected_count_.fetch_add(1, std::memory_order_relaxed);
            return std::unexpected(LevelerError::QueueFull);
        }

        auto now = std::chrono::steady_clock::now();
        uint64_t task_id = next_task_id_++;
        queue_.push(Task{
            .id = task_id,
            .payload = std::move(payload),
            .enqueue_time = now,
            .deadline = now + ttl
        });

        cv_not_empty_.notify_one();
        return task_id;
    }

    // Отримання задачі пулом воркерів з урахуванням дедлайну та ліміту темпу
    std::optional<Task> dequeue() {
        while (true) {
            std::unique_lock lock(mutex_);
            cv_not_empty_.wait(lock, [this] {
                return !queue_.empty() || shutdown_;
            });

            if (queue_.empty() && shutdown_) {
                return std::nullopt;
            }

            Task task = std::move(queue_.front());
            queue_.pop();
            lock.unlock();

            // Перевірка дедлайну задачі
            if (std::chrono::steady_clock::now() > task.deadline) {
                expired_count_.fetch_add(1, std::memory_order_relaxed);
                continue; // Задача застаріла під час очікування в черзі
            }

            // Обмеження темпу звернень до захищеного бекенду
            rate_limiter_.consume();
            processed_count_.fetch_add(1, std::memory_order_relaxed);

            return task;
        }
    }

    void stop() {
        std::unique_lock lock(mutex_);
        shutdown_ = true;
        cv_not_empty_.notify_all();
    }

    size_t depth() const {
        std::unique_lock lock(mutex_);
        return queue_.size();
    }

    uint64_t processed() const { return processed_count_.load(std::memory_order_relaxed); }
    uint64_t rejected()  const { return rejected_count_.load(std::memory_order_relaxed); }
    uint64_t expired()   const { return expired_count_.load(std::memory_order_relaxed); }

private:
    const size_t max_capacity_;
    TokenBucket rate_limiter_;

    mutable std::mutex mutex_;
    std::condition_variable cv_not_empty_;
    std::queue<Task> queue_;
    bool shutdown_{false};
    uint64_t next_task_id_{1};

    std::atomic<uint64_t> processed_count_{0};
    std::atomic<uint64_t> rejected_count_{0};
    std::atomic<uint64_t> expired_count_{0};
};

} // namespace resilience
