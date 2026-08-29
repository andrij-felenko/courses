// Порядкова статистика по вибірці затримок. Вибірка приходить як std::span:
// функція нічого не володіє й нічого не копіює — на стенді немає ні купи, ні
// зайвого кілобайта під другий буфер, тож сортування йде на місці.
#pragma once

#include <cstddef>
#include <optional>
#include <span>

#include "board.hpp"

namespace latency {

struct Summary {
    std::size_t count{0};
    std::size_t lost{0};
    board::Microseconds min{0};
    board::Microseconds max{0};
    board::Microseconds mean{0};
    board::Microseconds p50{0};
    board::Microseconds p95{0};
    board::Microseconds p99{0};
    board::Microseconds jitter{0}; // середнє відхилення від медіани
};

// std::nullopt — жодного успішного виміру, рахувати нічого.
// УВАГА: samples сортується на місці, порядок надходження втрачається.
[[nodiscard]] std::optional<Summary> analyse(std::span<board::Microseconds> samples,
                                             std::size_t lost) noexcept;

} // namespace latency
