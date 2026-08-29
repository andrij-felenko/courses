#pragma once

// Вотермарка стеку задачі.
//
// Область стеку приходить як std::span — межі та розмір їдуть разом, тож
// пари «вказівник + довжина» тут просто немає. Об'єкт володіє наглядом, а не
// пам'яттю: заливає шаблон при створенні й рахує незаймані слова на запит.

#include "budget/flags.hpp"

#include <cstddef>
#include <cstdint>
#include <span>
#include <string_view>

namespace budget {

class StackGuard {
public:
    static constexpr std::uint32_t kPattern = 0xA5A5A5A5u;

    // Заливає шаблон одразу: викликати лише для стеку, який ще не працює.
    StackGuard(std::string_view name, std::span<std::uint32_t> region,
               std::size_t reserve_bytes);

    [[nodiscard]] std::string_view name() const noexcept { return name_; }

    // Незайманий запас у байтах.
    [[nodiscard]] std::size_t free_bytes() const noexcept;

    // Чи ціле сторожове слово на дні області.
    [[nodiscard]] bool intact() const noexcept;

    [[nodiscard]] Budget audit() const noexcept;

private:
    std::string_view         name_;
    std::span<std::uint32_t> region_;
    std::size_t              reserve_bytes_;
};

struct StackAudit {
    Budget           flags{Budget::None};
    std::string_view worst_name{"—"};
    std::size_t      worst_free{0};
};

[[nodiscard]] StackAudit audit_stacks(std::span<const StackGuard> guards) noexcept;

} // namespace budget
