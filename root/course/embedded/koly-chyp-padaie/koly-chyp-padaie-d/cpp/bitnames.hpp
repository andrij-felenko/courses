#pragma once

#include <cstdint>
#include <span>
#include <string_view>

namespace diag {

// Пара «маска — людський опис». Таблиці цих пар описують і прапорці скидання,
// і біти статусних регістрів збою, тож перебір винесено в одне місце.
struct BitName {
    std::uint32_t    mask;
    std::string_view text;
};

template <typename Sink>
constexpr void for_each_set(std::span<const BitName> table, std::uint32_t value, Sink sink)
{
    for (const BitName& bit : table) {
        if ((value & bit.mask) != 0U) {
            sink(bit.text);
        }
    }
}

[[nodiscard]] constexpr bool any_set(std::span<const BitName> table, std::uint32_t value) noexcept
{
    for (const BitName& bit : table) {
        if ((value & bit.mask) != 0U) {
            return true;
        }
    }
    return false;
}

} // namespace diag
