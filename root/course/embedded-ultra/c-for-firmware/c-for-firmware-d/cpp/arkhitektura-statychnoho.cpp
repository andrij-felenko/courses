#include <cstdint>
#include <cstddef>
#include <span>
#include <optional>
#include <array>

// Ідіоматичний безпечний C++20 шаблонний кільцевий буфер без динамічної пам'яті
template <typename T, size_t Capacity>
class StaticRingBuffer {
    static_assert((Capacity > 0) && ((Capacity & (Capacity - 1)) == 0),
                  "Розмір кільцевого буфера має бути ступенем двійки!");
public:
    constexpr StaticRingBuffer() noexcept : head_(0), tail_(0) {}

    [[nodiscard]] bool empty() const noexcept {
        return head_ == tail_;
    }

    [[nodiscard]] bool full() const noexcept {
        return ((head_ + 1U) & mask_) == tail_;
    }

    [[nodiscard]] size_t size() const noexcept {
        return (head_ - tail_) & mask_;
    }

    [[nodiscard]] constexpr size_t capacity() const noexcept {
        return Capacity - 1U; // Одна комірка зарезервована під розрізнення full/empty
    }

    bool push(const T& item) noexcept {
        const size_t next_head = (head_ + 1U) & mask_;
        if (next_head == tail_) {
            return false; // Переповнення
        }
        buffer_[head_] = item;
        head_ = next_head;
        return true;
    }

    std::optional<T> pop() noexcept {
        if (empty()) {
            return std::nullopt;
        }
        T item = buffer_[tail_];
        tail_ = (tail_ + 1U) & mask_;
        return item;
    }

private:
    static constexpr size_t mask_ = Capacity - 1U;
    std::array<T, Capacity> buffer_{};
    volatile size_t head_{0};
    volatile size_t tail_{0};
};

// Екземпляр для прийому байтів телеметрії
inline StaticRingBuffer<uint8_t, 256> telemetry_rb;
