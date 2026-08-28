#include <vector>
#include <mutex>
#include <condition_variable>
#include <optional>
#include <expected>
#include <cstdint>
#include <concepts>
#include <system_error>

enum class DropPolicy {
    None,       // Блокуючий протитиск
    DropNewest, // Відхилення нових даних
    DropOldest  // Витіснення найстаріших даних (Head Drop)
};

enum class BufferError {
    Closed,
    BufferFull,
    InvalidWatermark
};

template <typename T>
class BoundedRingBuffer {
public:
    BoundedRingBuffer(size_t capacity, size_t hwm, size_t lwm)
        : capacity_(capacity),
          mask_(capacity - 1),
          hwm_(hwm),
          lwm_(lwm),
          buffer_(capacity) {
        if ((capacity & (capacity - 1)) != 0 || capacity == 0 || hwm > capacity || lwm >= hwm) {
            throw std::invalid_argument("Capacity must be power of 2 and 0 < LWM < HWM <= Capacity");
        }
    }

    ~BoundedRingBuffer() {
        close();
    }

    // Заборона копіювання
    BoundedRingBuffer(const BoundedRingBuffer&) = delete;
    BoundedRingBuffer& operator=(const BoundedRingBuffer&) = delete;

    void close() noexcept {
        std::unique_lock<std::mutex> lock(mutex_);
        is_closed_ = true;
        not_empty_cv_.notify_all();
        can_produce_cv_.notify_all();
    }

    // Блокуючий запис із гістерезисом
    std::expected<void, BufferError> push_blocking(T item) {
        std::unique_lock<std::mutex> lock(mutex_);

        while (!is_closed_) {
            const size_t count = tail_ - head_;

            if (count >= hwm_) {
                is_paused_ = true;
            }

            if (is_paused_) {
                can_produce_cv_.wait(lock, [this]() {
                    return is_closed_ || !is_paused_;
                });
                continue;
            }

            buffer_[tail_ & mask_] = std::move(item);
            ++tail_;

            not_empty_cv_.notify_one();
            return {};
        }

        return std::unexpected(BufferError::Closed);
    }

    // Неблокуючий запис із вибором політики скидання
    std::expected<void, BufferError> try_push(T item, DropPolicy policy = DropPolicy::DropNewest) {
        std::unique_lock<std::mutex> lock(mutex_);

        if (is_closed_) {
            return std::unexpected(BufferError::Closed);
        }

        const size_t count = tail_ - head_;

        if (count >= capacity_) {
            if (policy == DropPolicy::DropNewest) {
                return std::unexpected(BufferError::BufferFull);
            } else if (policy == DropPolicy::DropOldest) {
                ++head_; // Витісняємо найстаріший елемент
            }
        }

        buffer_[tail_ & mask_] = std::move(item);
        ++tail_;

        not_empty_cv_.notify_one();
        return {};
    }

    // Блокуюче читання споживача
    std::expected<T, BufferError> pop_blocking() {
        std::unique_lock<std::mutex> lock(mutex_);

        not_empty_cv_.wait(lock, [this]() {
            return is_closed_ || (tail_ > head_);
        });

        if (head_ == tail_ && is_closed_) {
            return std::unexpected(BufferError::Closed);
        }

        T item = std::move(buffer_[head_ & mask_]);
        ++head_;

        const size_t count = tail_ - head_;

        // Гістерезисне пробудження виробника при досягненні LWM
        if (is_paused_ && count <= lwm_) {
            is_paused_ = false;
            can_produce_cv_.notify_all();
        }

        return item;
    }

    [[nodiscard]] size_t size() const noexcept {
        std::unique_lock<std::mutex> lock(mutex_);
        return tail_ - head_;
    }

private:
    const size_t capacity_;
    const size_t mask_;
    const size_t hwm_;
    const size_t lwm_;

    std::vector<T> buffer_;
    size_t head_{0};
    size_t tail_{0};

    bool is_paused_{false};
    bool is_closed_{false};

    mutable std::mutex mutex_;
    std::condition_variable not_empty_cv_;
    std::condition_variable can_produce_cv_;
};
