#include <iostream>
#include <queue>
#include <mutex>
#include <condition_variable>
#include <optional>
#include <thread>
#include <vector>
#include <chrono>

template <typename T>
class BoundedQueue {
public:
    explicit BoundedQueue(std::size_t capacity)
        : capacity_(capacity), stopped_(false) {}

    ~BoundedQueue() {
        shutdown();
    }

    // Забороняємо копіювання для запобігання гонкам замків
    BoundedQueue(const BoundedQueue&) = delete;
    BoundedQueue& operator=(const BoundedQueue&) = delete;

    // Вставка елемента (блокування виробника при переповненні)
    bool push(T item) {
        std::unique_lock<std::mutex> lock(mtx_);
        
        // Очікуємо появу вільного місця або сигнал зупинки
        cv_not_full_.wait(lock, [this]() {
            return queue_.size() < capacity_ || stopped_;
        });

        if (stopped_) {
            return false; // Черга закрита для запису
        }

        queue_.push(std::move(item));

        // Сповіщаємо один із потоків-споживачів про появу елемента
        cv_not_empty_.notify_one();
        return true;
    }

    // Вилучення елемента (блокування споживача при порожній черзі)
    std::optional<T> pop() {
        std::unique_lock<std::mutex> lock(mtx_);

        // Очікуємо наявність елементів або сигнал зупинки
        cv_not_empty_.wait(lock, [this]() {
            return !queue_.empty() || stopped_;
        });

        if (queue_.empty() && stopped_) {
            return std::nullopt; // Черга порожня й закрита
        }

        T item = std::move(queue_.front());
        queue_.pop();

        // Сповіщаємо один із потоків-виробників про наявність вільного місця
        cv_not_full_.notify_one();
        return item;
    }

    // Сигнал чистого завершення роботи
    void shutdown() {
        {
            std::lock_guard<std::mutex> lock(mtx_);
            if (stopped_) return;
            stopped_ = true;
        }
        // Розблоковуємо абсолютно всі потоки в чергах сну
        cv_not_empty_.notify_all();
        cv_not_full_.notify_all();
    }

    std::size_t size() const {
        std::lock_guard<std::mutex> lock(mtx_);
        return queue_.size();
    }

private:
    const std::size_t capacity_;
    std::queue<T> queue_;
    mutable std::mutex mtx_;
    std::condition_variable cv_not_empty_;
    std::condition_variable cv_not_full_;
    bool stopped_;
};
