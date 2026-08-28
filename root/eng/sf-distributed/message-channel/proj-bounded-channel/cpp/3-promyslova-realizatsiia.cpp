#include <chrono>
#include <condition_variable>
#include <cstddef>
#include <mutex>
#include <optional>
#include <stdexcept>
#include <utility>
#include <vector>

template <typename T>
class BoundedChannel {
public:
    explicit BoundedChannel(std::size_t capacity)
        : capacity_(capacity), head_(0), tail_(0), count_(0), closed_(false) {
        if (capacity == 0) {
            throw std::invalid_argument("Capacity must be greater than zero");
        }
        buffer_.resize(capacity);
    }

    ~BoundedChannel() {
        close();
    }

    // Заборона небажаного копіювання каналу
    BoundedChannel(const BoundedChannel&) = delete;
    BoundedChannel& operator=(const BoundedChannel&) = delete;

    // Дозвіл переміщення
    BoundedChannel(BoundedChannel&&) noexcept = default;
    BoundedChannel& operator=(BoundedChannel&&) noexcept = default;

    // Блокуючий запис із підтримкою зворотного тиску
    bool send(T item) {
        std::unique_lock<std::mutex> lock(mutex_);
        not_full_cv_.wait(lock, [this]() {
            return count_ < capacity_ || closed_;
        });

        if (closed_) {
            return false;
        }

        buffer_[tail_] = std::move(item);
        tail_ = (tail_ + 1) % capacity_;
        ++count_;

        not_empty_cv_.notify_one();
        return true;
    }

    // Неблокуючий запис (Try-Send)
    bool try_send(T item) {
        std::unique_lock<std::mutex> lock(mutex_);
        if (closed_ || count_ == capacity_) {
            return false;
        }

        buffer_[tail_] = std::move(item);
        tail_ = (tail_ + 1) % capacity_;
        ++count_;

        not_empty_cv_.notify_one();
        return true;
    }

    // Блокуюче вичитування (Blocking Recv)
    std::optional<T> recv() {
        std::unique_lock<std::mutex> lock(mutex_);
        not_empty_cv_.wait(lock, [this]() {
            return count_ > 0 || closed_;
        });

        if (count_ == 0 && closed_) {
            return std::nullopt;
        }

        T item = std::move(buffer_[head_]);
        head_ = (head_ + 1) % capacity_;
        --count_;

        not_full_cv_.notify_one();
        return item;
    }

    // Неблокуюче вичитування (Try-Recv)
    std::optional<T> try_recv() {
        std::unique_lock<std::mutex> lock(mutex_);
        if (count_ == 0) {
            return std::nullopt;
        }

        T item = std::move(buffer_[head_]);
        head_ = (head_ + 1) % capacity_;
        --count_;

        not_full_cv_.notify_one();
        return item;
    }

    // Вичитування з обмеженням часу (Timed Recv)
    std::optional<T> recv_timeout(std::chrono::milliseconds timeout) {
        std::unique_lock<std::mutex> lock(mutex_);
        bool acquired = not_empty_cv_.wait_for(lock, timeout, [this]() {
            return count_ > 0 || closed_;
        });

        if (!acquired || (count_ == 0 && closed_)) {
            return std::nullopt;
        }

        T item = std::move(buffer_[head_]);
        head_ = (head_ + 1) % capacity_;
        --count_;

        not_full_cv_.notify_one();
        return item;
    }

    // Закриття каналу та пробудження всіх сплячих воркерів
    void close() {
        {
            std::lock_guard<std::mutex> lock(mutex_);
            if (closed_) return;
            closed_ = true;
        }
        not_empty_cv_.notify_all();
        not_full_cv_.notify_all();
    }

    [[nodiscard]] bool is_closed() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return closed_;
    }

    [[nodiscard]] std::size_t size() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return count_;
    }

    [[nodiscard]] std::size_t capacity() const noexcept {
        return capacity_;
    }

private:
    const std::size_t capacity_;
    std::vector<T> buffer_;
    std::size_t head_;
    std::size_t tail_;
    std::size_t count_;
    bool closed_;

    mutable std::mutex mutex_;
    std::condition_variable not_empty_cv_;
    std::condition_variable not_full_cv_;
};
