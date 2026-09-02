#pragma once

#include <concepts>
#include <cstdint>
#include <optional>

#include "fixed.hpp"

namespace dsp {

// Фільтр працює з будь-якою мілі-величиною драйвера, не знаючи її одиниць.
template <class Q>
concept Quantity = requires(Q q, std::int32_t c) {
    { q.count() } -> std::same_as<std::int32_t>;
    { Q{c} } -> std::same_as<Q>;
};

// Експоненційний фільтр низьких частот, alpha = 1/2^K: одне віднімання,
// один зсув, одне додавання. Стан — Q16.16, тож залишок ділення не гине
// і фільтр не застрягає, коли різниця падає нижче 2^K.
template <Quantity Q, int K = 3>
class ExpFilter {
    static_assert(K >= 0 && K <= 15, "зсув мусить лишити місце цілій частині");

public:
    constexpr Q update(Q sample) noexcept {
        const std::int32_t x = fx::saturate_bits<16>(sample.count());
        const std::int32_t x_q16 = x * static_cast<std::int32_t>(fx::Q16::one);

        if (!primed_) {
            // Перший відлік заряджає стан напряму — інакше фільтр повзе
            // до справжнього значення десятки періодів після ввімкнення.
            acc_ = fx::Q16::from_raw(x_q16);
            primed_ = true;
            return Q{x};
        }

        // Різниця двох крайніх значень Q16.16 не влазить в int32 —
        // саме тут наївний код тихо переповнюється.
        const std::int64_t diff = static_cast<std::int64_t>(x_q16) - acc_.raw();
        acc_ = fx::Q16::from_raw(
            fx::saturate(static_cast<std::int64_t>(acc_.raw()) + (diff >> K)));
        return Q{acc_.to_int()};
    }

    // Поки не було жодного відліку, значення не існує — і це видно з типу.
    [[nodiscard]] constexpr std::optional<Q> value() const noexcept {
        if (!primed_) {
            return std::nullopt;
        }
        return Q{acc_.to_int()};
    }

    constexpr void reset() noexcept {
        acc_ = fx::Q16{};
        primed_ = false;
    }

private:
    fx::Q16 acc_{};
    bool primed_{false};
};

// Показова «наївна» версія: стан у цілих, залишок губиться на кожному кроці.
template <int K>
[[nodiscard]] constexpr std::int16_t naive_update(std::int16_t& state, std::int16_t x) noexcept {
    const std::int32_t s = state;
    state = static_cast<std::int16_t>(fx::saturate_bits<16>(s + ((static_cast<std::int32_t>(x) - s) >> K)));
    return state;
}

} // namespace dsp
