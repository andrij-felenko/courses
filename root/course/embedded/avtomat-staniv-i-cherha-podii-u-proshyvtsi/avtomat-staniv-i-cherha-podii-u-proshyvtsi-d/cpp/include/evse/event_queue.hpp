#pragma once

#include <array>
#include <atomic>
#include <bit>
#include <cstddef>
#include <cstdint>
#include <optional>
#include <type_traits>

#include "evse/board.hpp"

namespace evse {

/*
 * Кільцева черга подій без блокувань. Один споживач — головний цикл; виробники
 * — обробники переривань.
 *
 * ProducerLock — політика взаємного витіснення виробників. Коли джерело одне
 * (або всі вони на однаковому рівні пріоритету NVIC і не витісняють одне
 * одного), досить NoLock, і push() не чіпає маску переривань узагалі. Коли
 * джерел кілька на різних пріоритетах — підставляється RAII-замок плати.
 */
template <class T, std::size_t Capacity, class ProducerLock = NoLock>
class EventQueue {
    static_assert(std::has_single_bit(Capacity),
                  "розмір мусить бути степенем двійки: перенесення індексу робиться маскою");
    static_assert(std::is_trivially_copyable_v<T>,
                  "запис черги заповнюється в перериванні й мусить копіюватися побайтово");

    static constexpr std::size_t kMask = Capacity - 1;

public:
    /* Викликається з обробника переривання. */
    bool push(const T& item) noexcept
    {
        [[maybe_unused]] const ProducerLock guard{};

        const auto head = head_.load(std::memory_order_relaxed);
        const auto next = (head + 1) & kMask;

        if (next == tail_.load(std::memory_order_acquire)) {
            /*
             * Затирати найстаріший запис не можна: у ньому міг бути перехід у
             * стан аварії. Відкидаємо новий і рахуємо втрату — головний цикл
             * побачить лічильник і знеструмить лінію.
             */
            dropped_.fetch_add(1, std::memory_order_relaxed);
            return false;
        }

        slots_[head] = item;

        /* Запис-звільнення: усі поля слоту мусять стати видимими до того, як
         * споживач побачить новий head. */
        head_.store(next, std::memory_order_release);
        return true;
    }

    /* Викликається виключно з головного циклу. */
    [[nodiscard]] std::optional<T> pop() noexcept
    {
        const auto tail = tail_.load(std::memory_order_relaxed);

        if (tail == head_.load(std::memory_order_acquire)) {
            return std::nullopt;
        }

        const T item = slots_[tail];

        /* Слот вважається вільним лише після того, як його скопійовано. */
        tail_.store((tail + 1) & kMask, std::memory_order_release);
        return item;
    }

    [[nodiscard]] bool empty() const noexcept
    {
        return head_.load(std::memory_order_acquire) == tail_.load(std::memory_order_relaxed);
    }

    [[nodiscard]] std::uint32_t dropped() const noexcept
    {
        return dropped_.load(std::memory_order_relaxed);
    }

    [[nodiscard]] static constexpr std::size_t capacity() noexcept { return Capacity - 1; }

private:
    std::array<T, Capacity>    slots_{};
    std::atomic<std::size_t>   head_{0};
    std::atomic<std::size_t>   tail_{0};
    std::atomic<std::uint32_t> dropped_{0};
};

} // namespace evse
