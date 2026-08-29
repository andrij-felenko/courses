#pragma once

// Контракт між повільним і швидким доменами — і безблокувальний канал під нього.

#include <atomic>
#include <chrono>
#include <cstdint>
#include <optional>

#include "geometry.hpp"

namespace flight {

using Micros = std::chrono::microseconds;

// Усе, що наведення каже регуляторові. Жодної навігаційної величини тут немає:
// ні координат NED, ні вейпойнтів, ні стану приймача GNSS.
struct Setpoint {
    Micros stamp{0};
    Quat qTarget{};
    Vec3 rateFeedForward{};
    float thrust{0.0F};
};

// Seqlock: письменник один (наведення, 50 Гц), читач один (регулятор, 1 кГц).
// Читач не блокується ніколи — переривання гіроскопа не має права чекати
// на м'ютекс, який тримає повільна задача навігації.
class SetpointMailbox {
public:
    void publish(const Setpoint& sp) noexcept {
        const std::uint32_t s = seq_.load(std::memory_order_relaxed);

        seq_.store(s + 1, std::memory_order_relaxed);        // непарне: запис триває
        std::atomic_thread_fence(std::memory_order_release);

        data_ = sp;

        std::atomic_thread_fence(std::memory_order_release);
        seq_.store(s + 2, std::memory_order_relaxed);        // парне: копія цілісна
    }

    // std::nullopt — даних ще не було або читання розірвав письменник.
    [[nodiscard]] std::optional<Setpoint> consume() const noexcept {
        for (int attempt = 0; attempt < kReadAttempts; ++attempt) {
            const std::uint32_t s0 = seq_.load(std::memory_order_acquire);
            if (s0 == 0 || (s0 & 1U) != 0U) {
                continue;
            }

            Setpoint sp = data_;

            std::atomic_thread_fence(std::memory_order_acquire);
            if (seq_.load(std::memory_order_relaxed) == s0) {
                return sp;
            }
            // Письменник ходить у 20 разів рідше — другий повтор уже екзотика.
        }
        return std::nullopt;
    }

private:
    static constexpr int kReadAttempts = 4;

    Setpoint data_{};
    std::atomic<std::uint32_t> seq_{0};
};

// Зворотний канал знизу вгору. Два біти, але без першого з них
// анти-вінд-ап зовнішнього контуру неможливий у принципі.
class ControlFeedback {
public:
    void setSaturated(bool on) noexcept { saturated_.store(on, std::memory_order_relaxed); }
    void setFallback(bool on) noexcept { fallback_.store(on, std::memory_order_relaxed); }

    [[nodiscard]] bool saturated() const noexcept { return saturated_.load(std::memory_order_relaxed); }
    [[nodiscard]] bool fallback() const noexcept { return fallback_.load(std::memory_order_relaxed); }

private:
    std::atomic<bool> saturated_{false};
    std::atomic<bool> fallback_{false};
};

}  // namespace flight
