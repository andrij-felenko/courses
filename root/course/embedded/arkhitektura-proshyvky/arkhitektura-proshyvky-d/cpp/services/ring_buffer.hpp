// services/ring_buffer.hpp — кільцевий буфер із розміром у типі.
// Шаблон замість покажчика на пам'ять і поля elem_size: місткість відома
// компіляторові, тож індекси лишаються в регістрах, а масив — усередині
// об'єкта. Купи немає, як і належить прошивці.
#pragma once

#include <array>
#include <cstddef>
#include <optional>
#include <utility>

namespace services {

template <typename T, std::size_t Capacity>
class RingBuffer {
    static_assert(Capacity > 0, "місткість буфера має бути додатною");

public:
    using value_type = T;

    [[nodiscard]] constexpr std::size_t capacity() const noexcept { return Capacity; }
    [[nodiscard]] constexpr std::size_t size() const noexcept { return count_; }
    [[nodiscard]] constexpr bool empty() const noexcept { return count_ == 0; }
    [[nodiscard]] constexpr bool full() const noexcept { return count_ == Capacity; }

    constexpr void clear() noexcept
    {
        head_ = 0;
        tail_ = 0;
        count_ = 0;
    }

    // false — буфера бракує; елемент НЕ зникає мовчки, рішення за викликачем.
    [[nodiscard]] constexpr bool push(const T& value)
    {
        if (full()) {
            return false;
        }
        storage_[head_] = value;
        head_ = advance(head_);
        ++count_;
        return true;
    }

    // Витісняє найстаріший елемент, коли місця немає. Повертає true,
    // якщо щось довелося викинути — лічильник втрат веде викликач.
    constexpr bool push_overwrite(const T& value)
    {
        bool dropped = false;
        if (full()) {
            tail_ = advance(tail_);
            --count_;
            dropped = true;
        }
        storage_[head_] = value;
        head_ = advance(head_);
        ++count_;
        return dropped;
    }

    [[nodiscard]] constexpr std::optional<T> pop()
    {
        if (empty()) {
            return std::nullopt;
        }
        T value = std::move(storage_[tail_]);
        tail_ = advance(tail_);
        --count_;
        return value;
    }

    [[nodiscard]] constexpr const T* peek() const noexcept
    {
        return empty() ? nullptr : &storage_[tail_];
    }

private:
    [[nodiscard]] static constexpr std::size_t advance(std::size_t index) noexcept
    {
        // Без ділення: на Cortex-M0 його немає в залізі.
        const std::size_t next = index + 1;
        return (next == Capacity) ? 0 : next;
    }

    std::array<T, Capacity> storage_{};
    std::size_t             head_{0};
    std::size_t             tail_{0};
    std::size_t             count_{0};
};

} // namespace services
