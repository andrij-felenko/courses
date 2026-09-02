#pragma once

#include <array>
#include <atomic>
#include <cstddef>
#include <cstdint>
#include <optional>

namespace input {

/* SPSC-черга (Single Producer, Single Consumer): push() кличе ЛИШЕ
   переривання таймера, pop() — ЛИШЕ головний цикл. Кожен індекс має одного
   власника, тому критична секція __disable_irq() не потрібна; порядок
   записів тримають acquire/release, а не вимкнені переривання.

   На Cortex-M std::atomic<std::size_t> лок-фрі: це звичайні ldr/str плюс
   бар'єр компілятора, жодних викликів бібліотеки. */
template <typename T, std::size_t Capacity>
class EventQueue {
    static_assert(Capacity >= 2 && (Capacity & (Capacity - 1)) == 0,
                  "місткість мусить бути степенем двійки: індекс згортаємо маскою");

public:
    /* Кладе подію. Повертає false, якщо черга повна: у перериванні чекати
       нема як, тож подію втрачаємо й лише рахуємо втрату. */
    bool push(const T& item) noexcept {
        const std::size_t head = head_.load(std::memory_order_relaxed);
        const std::size_t next = (head + 1) & Mask;
        if (next == tail_.load(std::memory_order_acquire)) {
            dropped_.fetch_add(1, std::memory_order_relaxed);
            return false;
        }
        buffer_[head] = item;
        head_.store(next, std::memory_order_release);  // дані вже видимі
        return true;
    }

    /* Порожня черга — не помилка, а звичайний стан. Тому optional, а не
       пара «код повернення + вихідний параметр». */
    [[nodiscard]] std::optional<T> pop() noexcept {
        const std::size_t tail = tail_.load(std::memory_order_relaxed);
        if (tail == head_.load(std::memory_order_acquire)) {
            return std::nullopt;
        }
        T item = buffer_[tail];
        tail_.store((tail + 1) & Mask, std::memory_order_release);
        return item;
    }

    /* Викидання залишків при зміні екрана. Тільки зі споживача: він власник
       tail, тож перегін безпечний навіть посеред запису з переривання. */
    void clear() noexcept {
        tail_.store(head_.load(std::memory_order_acquire), std::memory_order_release);
    }

    [[nodiscard]] std::size_t size() const noexcept {
        return (head_.load(std::memory_order_acquire) -
                tail_.load(std::memory_order_acquire)) & Mask;
    }

    [[nodiscard]] bool empty() const noexcept { return size() == 0; }

    [[nodiscard]] std::uint32_t dropped() const noexcept {
        return dropped_.load(std::memory_order_relaxed);
    }

private:
    /* Один слот завжди лишається порожнім — ціна за відмову від спільного
       лічильника, який довелося б захищати критичною секцією. */
    static constexpr std::size_t Mask = Capacity - 1;

    std::array<T, Capacity> buffer_{};
    std::atomic<std::size_t> head_{0};
    std::atomic<std::size_t> tail_{0};
    std::atomic<std::uint32_t> dropped_{0};
};

}  // namespace input
