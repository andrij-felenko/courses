#pragma once

#include <array>
#include <cstddef>
#include <optional>
#include <utility>

#include "at/critical_section.hpp"

namespace at {

/* Черга фіксованої місткості. Кладуть у неї з різних контекстів (головний
   цикл, URC-колбек, переривання), тому індекси рухаються під критичною
   секцією. Сам елемент лише переміщується — це кілька десятків байтів,
   і тримати переривання вимкненими на цей час дешевше, ніж городити
   двофазну вставку. */
template <typename T, std::size_t Capacity>
class StaticQueue {
public:
    static_assert(Capacity > 0);

    bool push(T value) noexcept
    {
        CriticalSection guard;
        if (count_ == Capacity) {
            return false;
        }
        slot_[head_] = std::move(value);
        head_ = (head_ + 1) % Capacity;
        ++count_;
        return true;
    }

    [[nodiscard]] std::optional<T> pop() noexcept
    {
        CriticalSection guard;
        if (count_ == 0) {
            return std::nullopt;
        }
        std::optional<T> taken{std::move(slot_[tail_])};
        slot_[tail_] = T{};   // звільняємо ресурси елемента, що поїхав
        tail_ = (tail_ + 1) % Capacity;
        --count_;
        return taken;
    }

    [[nodiscard]] std::size_t size() const noexcept { return count_; }
    [[nodiscard]] bool empty() const noexcept { return count_ == 0; }

private:
    std::array<T, Capacity> slot_{};
    std::size_t head_{0};
    std::size_t tail_{0};
    std::size_t count_{0};
};

}  // namespace at
