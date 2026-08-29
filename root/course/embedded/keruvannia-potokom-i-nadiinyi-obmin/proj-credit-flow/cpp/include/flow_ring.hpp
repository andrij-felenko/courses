// Кільцевий буфер приймача з гістерезисними порогами й керуванням лінією /RTS.
//
// Порівняно з версією на C тут дві заміни, і обидві не косметичні:
//   * ручний __DMB() зник — його роль виконує std::memory_order_release/acquire
//     на індексах, тобто те саме впорядкування, але виражене в мові, а не в асемблері;
//   * парні cpsid/cpsie замінено на IrqGuard, бо ранній return із гілки не має
//     права лишити переривання вимкненими.
#pragma once

#include <algorithm>
#include <array>
#include <atomic>
#include <concepts>
#include <cstddef>
#include <cstdint>
#include <optional>
#include <span>
#include <utility>

namespace flow {

// Вимикання переривань як ресурс: захоплюємо в конструкторі, віддаємо в деструкторі.
class IrqGuard {
public:
    IrqGuard() noexcept
    {
#if defined(__ARM_ARCH)
        __asm volatile("mrs %0, primask" : "=r"(primask_));
        __asm volatile("cpsid i" ::: "memory");
#else
        std::atomic_signal_fence(std::memory_order_seq_cst);
#endif
    }

    ~IrqGuard() noexcept
    {
#if defined(__ARM_ARCH)
        // Відновлюємо попередній стан, а не вмикаємо наосліп: нас могли викликати
        // вже під замком.
        if ((primask_ & 1U) == 0U) {
            __asm volatile("cpsie i" ::: "memory");
        }
#else
        std::atomic_signal_fence(std::memory_order_seq_cst);
#endif
    }

    IrqGuard(const IrqGuard&) = delete;
    IrqGuard& operator=(const IrqGuard&) = delete;

private:
    [[maybe_unused]] std::uint32_t primask_{0};
};

template <class T>
concept RtsLine = std::invocable<T, bool>;

// Line викликається з двох контекстів: із переривання (підняти Busy) і зі
// споживача (опустити в Ready). Тримати її треба такою, щоб виклик коштував
// один запис у регістр GPIO.
template <std::size_t Capacity, RtsLine Line>
class Ring {
    static_assert(Capacity >= 16 && (Capacity & (Capacity - 1)) == 0,
                  "місткість — степінь двійки, інакше маска індексу не працює");

public:
    static constexpr std::size_t kHighWatermark = Capacity * 3 / 4; // 192 зі 256
    static constexpr std::size_t kLowWatermark = Capacity / 4;      // 64 зі 256

    explicit Ring(Line line) noexcept : line_{std::move(line)} { line_(true); }

    // Контекст переривання прийому. Єдиний, кому дозволено рухати head_.
    [[nodiscard]] bool push_from_isr(std::uint8_t byte) noexcept
    {
        const auto head = head_.load(std::memory_order_relaxed);
        if (head - tail_.load(std::memory_order_acquire) >= Capacity) {
            overruns_.fetch_add(1, std::memory_order_relaxed);
            return false; // запас з'їдено: передавач не спинився вчасно
        }

        storage_[head & kMask] = byte;
        // release: байт лежить у пам'яті раніше, ніж споживач побачить індекс.
        head_.store(head + 1, std::memory_order_release);

        if (ready_.load(std::memory_order_relaxed) && level() >= kHighWatermark) {
            // Критична секція тут не потрібна: споживач свою перевірку робить із
            // вимкненими перериваннями, тож ми не влітаємо в її середину.
            ready_.store(false, std::memory_order_relaxed);
            line_(false);
        }
        return true;
    }

    // Контекст споживача. Єдиний, кому дозволено рухати tail_.
    [[nodiscard]] std::optional<std::uint8_t> pop() noexcept
    {
        const auto tail = tail_.load(std::memory_order_relaxed);
        if (head_.load(std::memory_order_acquire) == tail) {
            return std::nullopt;
        }

        const std::uint8_t byte = storage_[tail & kMask];
        // release: байт прочитано раніше, ніж слот оголошено вільним.
        tail_.store(tail + 1, std::memory_order_release);

        release_line();
        return byte;
    }

    // Вигрібання пачкою: один зсув tail_ і одна перевірка порога на всю пачку.
    [[nodiscard]] std::size_t pop(std::span<std::uint8_t> dst) noexcept
    {
        const auto tail = tail_.load(std::memory_order_relaxed);
        const auto available = head_.load(std::memory_order_acquire) - tail;
        const auto taken = static_cast<std::uint32_t>(
            std::min<std::size_t>(dst.size(), static_cast<std::size_t>(available)));

        for (std::uint32_t i = 0; i < taken; ++i) {
            dst[i] = storage_[(tail + i) & kMask];
        }
        if (taken == 0) {
            return 0;
        }

        tail_.store(tail + taken, std::memory_order_release);
        release_line();
        return taken;
    }

    [[nodiscard]] std::size_t level() const noexcept
    {
        // Різниця беззнакових правильна й після переповнення індексів.
        return static_cast<std::size_t>(head_.load(std::memory_order_relaxed) -
                                        tail_.load(std::memory_order_relaxed));
    }

    [[nodiscard]] std::size_t free_space() const noexcept { return Capacity - level(); }
    [[nodiscard]] bool ready() const noexcept { return ready_.load(std::memory_order_relaxed); }
    [[nodiscard]] std::uint32_t overruns() const noexcept
    {
        return overruns_.load(std::memory_order_relaxed);
    }

private:
    static constexpr std::uint32_t kMask = static_cast<std::uint32_t>(Capacity) - 1;

    // Перевірка рівня й перемикання лінії мусять бути однією неподільною дією:
    // інакше між ними встигає ISR, підніме Busy — а ми затремо його своїм Ready.
    void release_line() noexcept
    {
        const IrqGuard guard;
        if (!ready_.load(std::memory_order_relaxed) && level() <= kLowWatermark) {
            ready_.store(true, std::memory_order_relaxed);
            line_(true);
        }
    }

    std::array<std::uint8_t, Capacity> storage_{};
    std::atomic<std::uint32_t> head_{0};
    std::atomic<std::uint32_t> tail_{0};
    std::atomic<bool> ready_{true};
    std::atomic<std::uint32_t> overruns_{0};
    Line line_;
};

// Місткість не виводиться з аргументів, тож задаємо її фабрикою, а тип лінії
// хай компілятор виводить сам — лямбда чи функція, байдуже.
template <std::size_t Capacity, RtsLine Line>
[[nodiscard]] auto make_ring(Line line) noexcept
{
    return Ring<Capacity, Line>{std::move(line)};
}

} // namespace flow
