// SPSC кільцевий буфер без блокувань. Те саме, що й у версії мовою C, але
// впорядкування пам'яті задане не інструкцією DMB, а моделлю C++11:
// std::atomic зі семантикою release при публікації та acquire при читанні.
// Компілятор сам покладе туди dmb на ARM і нічого — на x86, де модель сильна.
#pragma once

#include <algorithm>
#include <array>
#include <atomic>
#include <cstddef>
#include <cstdint>
#include <optional>
#include <span>
#include <type_traits>

namespace rb {

// 32 байти на Cortex-M7, 64 на Cortex-A і x86. Беремо більше.
inline constexpr std::size_t kCacheLine = 64;

template <typename T, std::size_t Capacity>
    requires (std::is_trivially_copyable_v<T> && Capacity > 1 &&
              (Capacity & (Capacity - 1)) == 0)   // ємність — степінь двійки
class SpscRingBuffer {
public:
    using value_type = T;

    // Один слот зарезервовано під ознаку порожнечі head == tail.
    static constexpr std::size_t capacity() noexcept { return Capacity - 1; }

    // ---- сторона переривання: єдиний постачальник ----

    bool push_from_isr(const T& item) noexcept {
        const std::size_t head = head_.load(std::memory_order_relaxed);
        const std::size_t tail = tail_.load(std::memory_order_acquire);
        const std::size_t next = (head + 1) & kMask;

        if (next == tail) {
            dropped_.fetch_add(1, std::memory_order_relaxed);
            return false;   // переповнення: обробник не чекає, а рахує втрату
        }

        buffer_[head] = item;
        // release: запис елемента видно всім, хто побачив новий head
        head_.store(next, std::memory_order_release);
        return true;
    }

    // Пачка з апаратного FIFO: один release на всю пачку.
    std::size_t push_from_isr(std::span<const T> items) noexcept {
        std::size_t head = head_.load(std::memory_order_relaxed);
        const std::size_t tail = tail_.load(std::memory_order_acquire);
        std::size_t written = 0;

        for (const T& item : items) {
            const std::size_t next = (head + 1) & kMask;
            if (next == tail) {
                break;
            }
            buffer_[head] = item;
            head = next;
            ++written;
        }

        if (written != 0) {
            head_.store(head, std::memory_order_release);
        }
        if (written != items.size()) {
            dropped_.fetch_add(items.size() - written, std::memory_order_relaxed);
        }
        return written;
    }

    [[nodiscard]] std::uint64_t dropped() const noexcept {
        return dropped_.load(std::memory_order_relaxed);
    }

    // ---- сторона споживача ----

    // Порожньо — це не помилка, тому не виняток і не -1, а порожній optional.
    [[nodiscard]] std::optional<T> pop() noexcept {
        const std::size_t tail = tail_.load(std::memory_order_relaxed);
        const std::size_t head = head_.load(std::memory_order_acquire);

        if (tail == head) {
            return std::nullopt;
        }

        T item = buffer_[tail];
        // release: слот оголошено вільним лише після того, як елемент забрано
        tail_.store((tail + 1) & kMask, std::memory_order_release);
        return item;
    }

    std::size_t pop(std::span<T> out) noexcept {
        std::size_t tail = tail_.load(std::memory_order_relaxed);
        const std::size_t head = head_.load(std::memory_order_acquire);

        std::size_t ready = std::min((head - tail) & kMask, out.size());
        for (std::size_t i = 0; i < ready; ++i) {
            out[i] = buffer_[tail];
            tail = (tail + 1) & kMask;
        }

        if (ready != 0) {
            tail_.store(tail, std::memory_order_release);
        }
        return ready;
    }

    // Викинути найстаріші елементи, коли цінні лише найсвіжіші. Право на це
    // має саме споживач: tail належить йому, постачальник побачить лише
    // більше вільного місця.
    std::size_t discard_oldest(std::size_t count) noexcept {
        const std::size_t tail = tail_.load(std::memory_order_relaxed);
        const std::size_t head = head_.load(std::memory_order_acquire);
        const std::size_t drop = std::min(count, (head - tail) & kMask);

        if (drop != 0) {
            tail_.store((tail + drop) & kMask, std::memory_order_release);
        }
        return drop;
    }

    [[nodiscard]] std::size_t size() const noexcept {
        const std::size_t head = head_.load(std::memory_order_acquire);
        const std::size_t tail = tail_.load(std::memory_order_acquire);
        return (head - tail) & kMask;
    }

    [[nodiscard]] bool empty() const noexcept { return size() == 0; }

private:
    static constexpr std::size_t kMask = Capacity - 1;

    static_assert(std::atomic<std::size_t>::is_always_lock_free,
                  "індекси мусять бути справді без блокувань, інакше вся вигадка марна");

    alignas(kCacheLine) std::array<T, Capacity> buffer_{};

    // Лінія постачальника: head і лічильник втрат пише лише він.
    alignas(kCacheLine) std::atomic<std::size_t> head_{0};
    std::atomic<std::uint64_t> dropped_{0};

    // Лінія споживача — окрема, щоб запис у tail не інвалідував лінію з head
    // на іншому ядрі (хибне розділення, false sharing).
    alignas(kCacheLine) std::atomic<std::size_t> tail_{0};
};

}  // namespace rb
