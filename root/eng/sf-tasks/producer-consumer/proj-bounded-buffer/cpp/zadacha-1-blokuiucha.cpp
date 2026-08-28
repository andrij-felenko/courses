#include <mutex>
#include <condition_variable>
#include <vector>
#include <optional>
#include <cstddef>

template <typename T>
class BoundedQueue {
public:
    explicit BoundedQueue(std::size_t capacity)
        : buffer_(capacity), capacity_(capacity), head_(0), tail_(0), count_(0), is_closed_(false) {}

    ~BoundedQueue() {
        close();
    }

    // Заборона копіювання для збереження інваріантів м'ютекса
    BoundedQueue(const BoundedQueue&) = delete;
    BoundedQueue& operator=(const BoundedQueue&) = delete;

    bool push(T item) {
        std::unique_lock<std::mutex> lock(mutex_);
        // Цикл очікування наявності вільних місць або сигналу закриття
        not_full_cv_.wait(lock, [this] {
            return count_ < capacity_ || is_closed_;
        });

        if (is_closed_) {
            return false;
        }

        buffer_[tail_] = std::move(item);
        tail_ = (tail_ + 1) % capacity_;
        ++count_;

        not_empty_cv_.notify_one();
        return true;
    }

    std::optional<T> pop() {
        std::unique_lock<std::mutex> lock(mutex_);
        // Очікуємо появи елементів або закриття черги
        not_empty_cv_.wait(lock, [this] {
            return count_ > 0 || is_closed_;
        });

        if (count_ == 0 && is_closed_) {
            return std::nullopt; // Черга закрита та вичерпана
        }

        T item = std::move(buffer_[head_]);
        head_ = (head_ + 1) % capacity_;
        --count_;

        not_full_cv_.notify_one();
        return item;
    }

    void close() noexcept {
        {
            std::lock_guard<std::mutex> lock(mutex_);
            if (is_closed_) return;
            is_closed_ = true;
        }
        not_empty_cv_.notify_all();
        not_full_cv_.notify_all();
    }

    [[nodiscard]] std::size_t size() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return count_;
    }

private:
    std::vector<T> buffer_;
    const std::size_t capacity_;
    std::size_t head_;
    std::size_t tail_;
    std::size_t count_;
    bool is_closed_;

    mutable std::mutex mutex_;
    std::condition_variable not_empty_cv_;
    std::condition_variable not_full_cv_;
};
