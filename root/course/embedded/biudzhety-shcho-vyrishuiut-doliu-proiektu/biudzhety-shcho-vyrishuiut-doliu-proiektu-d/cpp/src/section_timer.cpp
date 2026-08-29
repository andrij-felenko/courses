#include "budget/section_timer.hpp"

#include <algorithm>

namespace budget {

void SectionBudget::commit(Clock::duration elapsed) noexcept
{
    const auto us = std::chrono::duration_cast<std::chrono::microseconds>(elapsed);

    last_ = us;
    total_ += us;
    ++runs_;
    worst_ = std::max(worst_, us);

    if (us > deadline_) {
        ++overruns_;
    }
}

std::chrono::microseconds SectionBudget::average() const noexcept
{
    if (runs_ == 0) {
        return std::chrono::microseconds{0};
    }
    return total_ / runs_;
}

SectionAudit audit_sections(std::span<const SectionBudget> sections) noexcept
{
    SectionAudit result;
    auto worst_margin = std::chrono::microseconds::max();

    for (const SectionBudget& section : sections) {
        result.flags |= section.audit();

        if (section.runs() > 0 && section.margin() < worst_margin) {
            worst_margin  = section.margin();
            result.worst  = &section;
        }
    }
    return result;
}

} // namespace budget
