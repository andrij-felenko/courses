// Кільце SPSC на std::atomic.
//
// У C-версії порядок запису тримає ручний DMB, а видимість — volatile.
// Тут обидві задачі бере на себе модель пам'яті: release при публікації
// індексу і acquire при його читанні. Компілятор сам поставить DMB там,
// де він потрібен, і не поставить там, де ні.
#pragma once

#include <array>
#include <atomic>
#include <cstddef>
#include <cstdint>
#include <optional>
#include <span>

namespace isr {

template <typename T, std::size_t Capacity>
class SpscRing {
    static_assert(Capacity >= 2 && (Capacity & (Capacity - 1)) == 0,
                  "місткість мусить бути степенем двійки: маска заміняє ділення");
    static_assert(Capacity <= 256,
                  "індекс однобайтовий — його читання мусить бути неподільним");

public:
    using index_type = std::uint8_t;
    static constexpr index_type kMask = static_cast<index_type>(Capacity - 1);

    // Викликається з обробника. false — кільце повне, елемент відкинуто.
    // noexcept не прикраса: у контексті переривання розкручувати стек нема куди.
    bool push_from_isr(T value) noexcept
    {
        const index_type head = head_.load(std::memory_order_relaxed);
        const index_type next = static_cast<index_type>((head + 1) & kMask);

        if (next == tail_.load(std::memory_order_acquire)) {
            return false;
        }

        storage_[head] = value;
        // release: запис елемента стане видимим споживачеві раніше,
        // ніж новий head. Саме сюди компілятор і вставить dmb.
        head_.store(next, std::memory_order_release);
        return true;
    }

    // Викликається з фонового завдання.
    std::optional<T> pop() noexcept
    {
        const index_type tail = tail_.load(std::memory_order_relaxed);

        if (tail == head_.load(std::memory_order_acquire)) {
            return std::nullopt;
        }

        T value = storage_[tail];
        tail_.store(static_cast<index_type>((tail + 1) & kMask), std::memory_order_release);
        return value;
    }

    // Пакетне вичитування: віддає ЗАПОВНЕНУ частину переданого буфера.
    // Замість пари «вказівник + довжина» повертаємо span — довжину
    // й пам'ять уже не можна розсинхронізувати.
    [[nodiscard]] std::span<T> drain(std::span<T> out) noexcept
    {
        std::size_t written = 0;
        while (written < out.size()) {
            const std::optional<T> item = pop();
            if (!item.has_value()) {
                break;
            }
            out[written++] = *item;
        }
        return out.first(written);
    }

    [[nodiscard]] index_type size() const noexcept
    {
        return static_cast<index_type>(head_.load(std::memory_order_relaxed) -
                                       tail_.load(std::memory_order_relaxed));
    }

private:
    std::array<T, Capacity> storage_{};
    std::atomic<index_type> head_{0};
    std::atomic<index_type> tail_{0};

    static_assert(std::atomic<index_type>::is_always_lock_free,
                  "атомарний індекс не має права ховати за собою замок");
};

} // namespace isr
