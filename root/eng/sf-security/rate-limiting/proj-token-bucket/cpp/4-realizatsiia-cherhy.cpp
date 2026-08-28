#include <queue>
#include <mutex>
#include <condition_variable>
#include <chrono>
#include <thread>
#include <optional>

template <typename T>
class LeakyBucketQueue {
public:
    explicit LeakyBucketQueue(size_t capacity, std::chrono::microseconds leak_interval)
        : capacity_(capacity), leak_interval_(leak_interval), stopped_(false) {}

    bool try_push(T item) {
        std::lock_guard<std::mutex> lock(mutex_);
        if (queue_.size() >= capacity_) {
            return false; // Черга переповнена
        }
        queue_.push(std::move(item));
        cv_not_empty_.notify_one();
        return true;
    }

    std::optional<T> pop_shaped() {
        std::unique_lock<std::mutex> lock(mutex_);
        cv_not_empty_.wait(lock, [this]() { return !queue_.empty() || stopped_; });

        if (stopped_ && queue_.empty()) {
            return std::nullopt;
        }

        T item = std::move(queue_.front());
        queue_.pop();
        lock.unlock();

        // Шейпінг: фіксований темп видачі завдань
        std::this_thread::sleep_for(leak_interval_);
        return item;
    }

    void stop() {
        std::lock_guard<std::mutex> lock(mutex_);
        stopped_ = true;
        cv_not_empty_.notify_all();
    }

private:
    const size_t capacity_;
    const std::chrono::microseconds leak_interval_;
    std::queue<T> queue_;
    std::mutex mutex_;
    std::condition_variable cv_not_empty_;
    bool stopped_;
};
