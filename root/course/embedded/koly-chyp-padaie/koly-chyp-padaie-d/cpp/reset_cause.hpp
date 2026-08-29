#pragma once

#include <cstdint>

namespace reset {

enum class Source : std::uint32_t {
    None     = 0U,
    PowerOn  = 1U << 0U,
    Brownout = 1U << 1U,
    Pin      = 1U << 2U,
    Iwdg     = 1U << 3U,
    Wwdg     = 1U << 4U,
    Software = 1U << 5U,
    LowPower = 1U << 6U
};

[[nodiscard]] constexpr Source operator|(Source lhs, Source rhs) noexcept
{
    return static_cast<Source>(static_cast<std::uint32_t>(lhs) | static_cast<std::uint32_t>(rhs));
}

constexpr Source& operator|=(Source& lhs, Source rhs) noexcept
{
    lhs = lhs | rhs;
    return lhs;
}

[[nodiscard]] constexpr bool contains(Source set, Source what) noexcept
{
    return (static_cast<std::uint32_t>(set) & static_cast<std::uint32_t>(what)) != 0U;
}

// Знімок причини перезапуску разом із сирим значенням RCC->CSR.
class Causes {
public:
    constexpr Causes() noexcept = default;
    constexpr Causes(Source sources, std::uint32_t raw_csr) noexcept
        : sources_{sources}
        , raw_csr_{raw_csr}
    {
    }

    [[nodiscard]] constexpr bool has(Source what) const noexcept { return contains(sources_, what); }
    [[nodiscard]] constexpr std::uint32_t raw_csr() const noexcept { return raw_csr_; }
    [[nodiscard]] constexpr bool empty() const noexcept { return sources_ == Source::None; }

    // Сторож або SYSRESETREQ означають, що попереднє життя обірвав крах,
    // а не звичайна подача живлення.
    [[nodiscard]] constexpr bool looks_like_crash() const noexcept
    {
        return has(Source::Iwdg) || has(Source::Wwdg) || has(Source::Software);
    }

    void print() const;

private:
    Source        sources_{Source::None};
    std::uint32_t raw_csr_{};
};

// Зчитує RCC->CSR і НЕГАЙНО стирає липкі прапорці бітом RMVF.
// Викликати першою дією в main(): друге звертання поверне ту саму копію,
// бо апаратура після RMVF уже нічого не пам'ятає.
[[nodiscard]] const Causes& capture();

} // namespace reset
