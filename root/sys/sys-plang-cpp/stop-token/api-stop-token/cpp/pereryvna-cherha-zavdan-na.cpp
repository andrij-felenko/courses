#include <condition_variable>
#include <mutex>
#include <queue>
#include <stop_token>
#include <iostream>

template<typename T>
class InterruptibleQueue {
    std::queue<T> queue_;
    mutable std::mutex mutex_;
    std::condition_variable_any cv_;

public:
    void push(T value) {
        {
            std::lock_guard lock(mutex_);
            queue_.push(std::move(value));
        }
        cv_.notify_one();
    }

    bool pop(T& value, std::stop_token stoken) {
        std::unique_lock lock(mutex_);
        // Очікування завершується при надходженні елемента АБО сигналу скасування
        bool success = cv_.wait(lock, stoken, [this] {
            return !queue_.empty();
        });

        if (!success || queue_.empty()) {
            return false; // Скасовано або черга порожня
        }

        value = std::move(queue_.front());
        queue_.pop();
        return true;
    }
};
