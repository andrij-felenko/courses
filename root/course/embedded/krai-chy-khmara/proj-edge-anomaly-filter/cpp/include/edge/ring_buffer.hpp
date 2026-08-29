#pragma once

#include <algorithm>
#include <array>
#include <cstddef>
#include <span>

namespace edge {

/**
 * Кільцевий буфер передісторії: сховище всередині об'єкта, купа не потрібна.
 * Розмір — параметр шаблона, тож він відомий компонувальнику й потрапляє
 * прямо в BSS разом з екземпляром детектора.
 */
template <typename T, std::size_t Capacity>
    requires(Capacity > 0)
class RingBuffer {
public:
    constexpr RingBuffer() noexcept = default;

    /// Пише елемент, найстаріший витісняє. Перезапис — штатний режим.
    constexpr void push(const T& item) noexcept
    {
        storage_[head_] = item;
        head_ = (head_ + 1) % Capacity;
        if (count_ < Capacity) {
            ++count_;
        }
    }

    /// Розгортає кільце в лінійний відрізок від найстарішого до найновішого.
    /// Повертає, скільки елементів насправді записано.
    constexpr std::size_t copy_oldest_first(std::span<T> dest) const noexcept
    {
        const std::size_t n = std::min(dest.size(), count_);
        std::size_t idx = (head_ + Capacity - count_) % Capacity;
        for (std::size_t i = 0; i < n; ++i) {
            dest[i] = storage_[idx];
            idx = (idx + 1) % Capacity;
        }
        return n;
    }

    [[nodiscard]] constexpr std::size_t size() const noexcept { return count_; }
    [[nodiscard]] constexpr bool full() const noexcept { return count_ == Capacity; }
    [[nodiscard]] static constexpr std::size_t capacity() noexcept { return Capacity; }

    constexpr void clear() noexcept
    {
        head_  = 0;
        count_ = 0;
        // Саме сховище не чистимо: за межами count_ його ніхто не читає.
    }

private:
    std::array<T, Capacity> storage_{};
    std::size_t head_{0};
    std::size_t count_{0};
};

}  // namespace edge
