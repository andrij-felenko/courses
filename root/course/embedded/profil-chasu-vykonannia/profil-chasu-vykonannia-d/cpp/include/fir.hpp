// Короткий FIR-фільтр. Довжина — параметр шаблону, тож і зсув лінії
// затримки, і скалярний добуток розгортаються згорткою пакета:
// у машинному коді лишається пряма послідовність VMLA без жодного переходу.
#pragma once

#include <array>
#include <bit>
#include <cstddef>
#include <cstdint>
#include <span>
#include <utility>

#include "stm32f4xx.h"   // __SMLAD, __SSAT

namespace prof {

template <std::size_t N>
class FirFilter {
    static_assert(N >= 2U, "фільтр коротший за два відліки не має сенсу");

public:
    constexpr explicit FirFilter(const std::array<float, N>& taps) noexcept : h_{taps} {}

    // Тіло лишається в заголовку навмисно: воно мусить вбудуватися в те
    // місце виклику, яке компонувальник кладе в секцію .ramfunc.
    float push(float sample) noexcept
    {
        shift(std::make_index_sequence<N - 1U>{});
        x_[0] = sample;
        return dot(std::make_index_sequence<N>{});
    }

    void reset() noexcept { x_.fill(0.0f); }

private:
    template <std::size_t... Is>
    void shift(std::index_sequence<Is...>) noexcept
    {
        // Згортка через кому виконується зліва направо: x[N-1] = x[N-2], ...
        ((x_[N - 1U - Is] = x_[N - 2U - Is]), ...);
    }

    template <std::size_t... Is>
    [[nodiscard]] float dot(std::index_sequence<Is...>) const noexcept
    {
        return ((x_[Is] * h_[Is]) + ...);
    }

    std::array<float, N> h_{};
    std::array<float, N> x_{};
};

// Та сама згортка в Q15 на парних інструкціях DSP: __SMLAD бере пару
// 16-бітних чисел, упакованих в один 32-бітний регістр, і за один такт
// робить два множення й два додавання.
[[nodiscard]] inline std::int32_t fir_q15_dot4(std::span<const std::int16_t, 4> x,
                                               std::span<const std::int16_t, 4> h) noexcept
{
    const auto pack = [](std::int16_t lo, std::int16_t hi) noexcept {
        return std::bit_cast<std::uint32_t>(std::array<std::int16_t, 2>{lo, hi});
    };

#if defined(__ARM_FEATURE_DSP) && (__ARM_FEATURE_DSP == 1)
    std::uint32_t acc = 0U;
    acc = __SMLAD(pack(x[0], x[1]), pack(h[0], h[1]), acc);
    acc = __SMLAD(pack(x[2], x[3]), pack(h[2], h[3]), acc);
    return static_cast<std::int32_t>(acc);
#else
    (void)pack;
    std::int32_t acc = 0;
    for (std::size_t i = 0U; i < 4U; ++i) {
        acc += static_cast<std::int32_t>(x[i]) * static_cast<std::int32_t>(h[i]);
    }
    return acc;
#endif
}

// Насичення однією інструкцією замість пари порівнянь із переходами.
[[nodiscard]] inline std::int16_t fir_q15_saturate(std::int32_t acc) noexcept
{
#if defined(__ARM_FEATURE_DSP) && (__ARM_FEATURE_DSP == 1)
    return static_cast<std::int16_t>(__SSAT(acc >> 15, 16));
#else
    const std::int32_t v = acc >> 15;
    return static_cast<std::int16_t>(v > 32767 ? 32767 : (v < -32768 ? -32768 : v));
#endif
}

}  // namespace prof
