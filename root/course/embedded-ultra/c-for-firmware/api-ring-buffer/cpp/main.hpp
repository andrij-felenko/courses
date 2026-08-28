#ifndef STATIC_RING_BUFFER_HPP
#define STATIC_RING_BUFFER_HPP

#include <cstdint>
#include <cstddef>
#include <array>
#include <optional>
#include <span>

template <typename T, size_t Capacity>
class StaticRingBuffer {
    static_assert((Capacity > 1) && ((Capacity & (Capacity - 1)) == 0),
                  "Capacity must be a power of two greater than 1!");
public:
    using value_type = T;
    using size_type  = size_t;

    constexpr StaticRingBuffer() noexcept = default;

    /**
     * @brief Скидає індекси буфера до початкового стану.
     */
    void clear() noexcept {
        head_ = 0;
        tail_ = 0;
    }

    /**
     * @brief Додає елемент у буфер без блокування переривань.
     * @return true у разі успіху, false якщо буфер заповнений.
     */
    bool push(const T& item) noexcept {
        const size_type next_head = (head_ + 1U) & mask_;
        if (next_head == tail_) {
            return false;
        }
        buffer_[head_] = item;
        head_ = next_head;
        return true;
    }

    /**
     * @brief Вилучає елемент із буфера.
     * @return std::optional з елементом або std::nullopt, якщо буфер порожній.
     */
    [[nodiscard]] std::optional<T> pop() noexcept {
        if (empty()) {
            return std::nullopt;
        }
        T item = buffer_[tail_];
        tail_ = (tail_ + 1U) & mask_;
        return item;
    }

    [[nodiscard]] bool empty() const noexcept {
        return head_ == tail_;
    }

    [[nodiscard]] bool full() const noexcept {
        return ((head_ + 1U) & mask_) == tail_;
    }

    [[nodiscard]] size_type size() const noexcept {
        return (head_ - tail_) & mask_;
    }

    [[nodiscard]] constexpr size_type capacity() const noexcept {
        return Capacity - 1U; // Одна комірка резервується для розрізнення full/empty
    }

private:
    static constexpr size_type mask_ = Capacity - 1U;
    std::array<T, Capacity> buffer_{};
    volatile size_type head_{0};
    volatile size_type tail_{0};
};

#endif // STATIC_RING_BUFFER_HPP
