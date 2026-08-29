#pragma once

#include <array>
#include <cstdint>
#include <expected>

#include "boot_status.hpp"
#include "manifest.hpp"

namespace boot {

// Біти відкликання: один рядок перемичок, по біту на слот ключа.
inline constexpr std::uint8_t kRevokeKey0 = 1U << 0;
inline constexpr std::uint8_t kRevokeKey1 = 1U << 1;
inline constexpr std::uint8_t kRevokeKey2 = 1U << 2;
inline constexpr std::uint8_t kRevokeKey3 = 1U << 3;

// Лічильник анти-відкату закодовано термометром: значення = кількість спалених бітів.
inline constexpr std::uint32_t kCounterBits = 32;

// Тіньова копія перемичок у SRAM: читаємо один раз на старті, бо ланцюг
// перевірок торкається тих самих полів по кілька разів.
struct EfuseMirror {
    std::array<Digest, kKeySlots> rootKeyDigest{};
    std::uint8_t revocationMask{};
    std::uint32_t monotonicCounter{};

    [[nodiscard]] bool isRevoked(std::uint8_t slot) const noexcept
    {
        return (revocationMask & static_cast<std::uint8_t>(1U << slot)) != 0;
    }
};

class Efuse {
public:
    [[nodiscard]] static std::expected<EfuseMirror, Status> readMirror() noexcept;

    // Незворотно палить біт відкликання слота: перевірка детектора просідання
    // напруги до імпульсу, контрольне зчитування у звичайному й граничному
    // режимах після нього.
    [[nodiscard]] static std::expected<void, Status> burnRevocation(std::uint8_t slot) noexcept;

    // Піднімає апаратний лічильник до version, допалюючи бракуючі біти термометра.
    [[nodiscard]] static std::expected<void, Status> burnCounter(std::uint32_t version) noexcept;
};

} // namespace boot
