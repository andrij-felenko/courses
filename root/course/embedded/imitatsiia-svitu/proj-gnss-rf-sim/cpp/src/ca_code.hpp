// ca_code.hpp — далекомірний код Голда. Код кожного апарата відомий наперед,
// тож рахуємо його на етапі компіляції й тримаємо готовими знаками ±1.
#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <optional>

namespace gnss {

inline constexpr std::size_t kCaCodeLength = 1023;
inline constexpr double      kCaChipRateHz = 1023000.0;

using CaCode = std::array<std::int8_t, kCaCodeLength>;   // +1 / −1, готові до множення

// Пара відводів регістра G2 — саме вона розрізняє апарати.
inline constexpr std::array<std::array<int, 2>, 32> kG2Taps{{
    {2,6},{3,7},{4,8},{5,9},{1,9},{2,10},{1,8},{2,9},{3,10},{2,3},
    {3,4},{5,6},{6,7},{7,8},{8,9},{9,10},{1,4},{2,5},{3,6},{4,7},
    {5,8},{6,9},{1,3},{4,6},{5,7},{6,8},{7,9},{8,10},{1,6},{2,7},
    {3,8},{4,9}
}};

[[nodiscard]] constexpr std::optional<CaCode> make_ca_code(int prn) noexcept
{
    if (prn < 1 || prn > 32) return std::nullopt;

    std::array<int, 11> g1{}, g2{};        // індексація з одиниці, як у стандарті
    for (int i = 1; i <= 10; ++i) g1[i] = g2[i] = 1;

    const auto [t1, t2] = kG2Taps[static_cast<std::size_t>(prn - 1)];

    CaCode code{};
    for (auto& chip : code) {
        const int bit = g1[10] ^ g2[static_cast<std::size_t>(t1)] ^ g2[static_cast<std::size_t>(t2)];
        chip = static_cast<std::int8_t>(1 - 2 * bit);

        const int fb1 = g1[3] ^ g1[10];
        const int fb2 = g2[2] ^ g2[3] ^ g2[6] ^ g2[8] ^ g2[9] ^ g2[10];
        for (int k = 10; k > 1; --k) { g1[k] = g1[k - 1]; g2[k] = g2[k - 1]; }
        g1[1] = fb1;
        g2[1] = fb2;
    }
    return code;
}

}  // namespace gnss
