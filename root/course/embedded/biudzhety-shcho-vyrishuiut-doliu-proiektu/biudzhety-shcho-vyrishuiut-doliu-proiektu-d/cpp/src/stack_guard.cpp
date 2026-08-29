#include "budget/stack_guard.hpp"

#include <algorithm>
#include <limits>
#include <stdexcept>

namespace budget {

StackGuard::StackGuard(std::string_view name, std::span<std::uint32_t> region,
                       std::size_t reserve_bytes)
    : name_{name}, region_{region}, reserve_bytes_{reserve_bytes}
{
    if (region_.size() < 2) {
        throw std::invalid_argument{"область стеку менша за два слова"};
    }
    std::ranges::fill(region_, kPattern);
}

std::size_t StackGuard::free_bytes() const noexcept
{
    // Стек росте вниз, тож незаймані слова лежать від дна області.
    const auto broken = std::ranges::find_if(
        region_, [](std::uint32_t word) { return word != kPattern; });

    const auto intact_words =
        static_cast<std::size_t>(std::ranges::distance(region_.begin(), broken));
    return intact_words * sizeof(std::uint32_t);
}

bool StackGuard::intact() const noexcept
{
    return region_.front() == kPattern;
}

Budget StackGuard::audit() const noexcept
{
    if (!intact()) {
        return Budget::StackOverflow;
    }
    return (free_bytes() < reserve_bytes_) ? Budget::StackLow : Budget::None;
}

StackAudit audit_stacks(std::span<const StackGuard> guards) noexcept
{
    StackAudit result;
    result.worst_free = std::numeric_limits<std::size_t>::max();

    for (const StackGuard& guard : guards) {
        result.flags |= guard.audit();

        const std::size_t free = guard.free_bytes();
        if (free < result.worst_free) {
            result.worst_free = free;
            result.worst_name = guard.name();
        }
    }

    if (guards.empty()) {
        result.worst_free = 0;
    }
    return result;
}

} // namespace budget
