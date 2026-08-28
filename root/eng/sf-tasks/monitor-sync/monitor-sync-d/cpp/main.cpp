#include <mutex>
#include <condition_variable>
#include <vector>
#include <stdexcept>

template <typename T>
class BoundedQueue {
public:
    explicit BoundedQueue(size_t capacity)
        : capacity_(capacity), head_(0), tail_(0), count_(0), buffer_(capacity) {
        if (capacity == 0) {
            throw std::invalid_argument("Capacity must be positive");
        }
    }

    void push(T item) {
        std::unique_lock<std::mutex> lock(mutex_);
        /* Лямбда гарантує перевірку умови у циклі while */
        not_full_.wait(lock, [this] { return count_ < capacity_; });

        buffer_[tail_] = std::move(item);
        tail_ = (tail_ + 1) % capacity_;
        ++count_;

        not_empty_.notify_one();
    }

    T pop() {
        std::unique_lock<std::mutex> lock(mutex_);
        /* Безпечне очікування з автоматичним повторним взяттям замка */
        not_empty_.wait(lock, [this] { return count_ > 0; });

        T item = std::move(buffer_[head_]);
        head_ = (head_ + 1) % capacity_;
        --count_;

        not_full_.notify_one();
        return item;
    }

private:
    const size_t capacity_;
    size_t head_;
    size_t tail_;
    size_t count_;
    std::vector<T> buffer_;

    std::mutex mutex_;
    std::condition_variable not_empty_;
    std::condition_variable not_full_;
};
