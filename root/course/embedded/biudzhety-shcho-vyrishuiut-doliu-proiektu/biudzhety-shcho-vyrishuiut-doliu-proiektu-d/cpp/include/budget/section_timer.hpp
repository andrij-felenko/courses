#pragma once

// Часовий бюджет критичної секції.
//
// Замість пари begin/end — вартовий на стеку: вимір закривається виходом з
// області видимості, і жодне дострокове return чи виняток посеред секції не
// лишить лічильник відкритим назавжди.

#include "budget/flags.hpp"

#include <chrono>
#include <cstdint>
#include <span>
#include <stdexcept>
#include <string_view>

namespace budget {

class SectionBudget {
public:
    using Clock = std::chrono::steady_clock;

    SectionBudget(std::string_view name, std::chrono::microseconds deadline)
        : name_{name}, deadline_{deadline}
    {
        if (deadline_.count() <= 0) {
            throw std::invalid_argument{"термін секції має бути додатним"};
        }
    }

    class Scope {
    public:
        explicit Scope(SectionBudget& owner) noexcept
            : owner_{&owner}, started_{Clock::now()} {}

        Scope(const Scope&)            = delete;
        Scope& operator=(const Scope&) = delete;

        Scope(Scope&& other) noexcept
            : owner_{other.owner_}, started_{other.started_}
        {
            other.owner_ = nullptr;
        }
        Scope& operator=(Scope&&) = delete;

        ~Scope()
        {
            if (owner_ != nullptr) {
                owner_->commit(Clock::now() - started_);
            }
        }

    private:
        SectionBudget*    owner_;
        Clock::time_point started_;
    };

    [[nodiscard]] Scope measure() noexcept { return Scope{*this}; }

    [[nodiscard]] std::string_view name() const noexcept { return name_; }
    [[nodiscard]] std::chrono::microseconds deadline() const noexcept { return deadline_; }
    [[nodiscard]] std::chrono::microseconds last() const noexcept { return last_; }
    [[nodiscard]] std::chrono::microseconds worst() const noexcept { return worst_; }
    [[nodiscard]] std::chrono::microseconds average() const noexcept;

    // Запас від найгіршого випадку до терміну; від'ємний — термін зірвано.
    [[nodiscard]] std::chrono::microseconds margin() const noexcept
    {
        return deadline_ - worst_;
    }

    [[nodiscard]] std::uint32_t runs() const noexcept { return runs_; }
    [[nodiscard]] std::uint32_t overruns() const noexcept { return overruns_; }

    [[nodiscard]] Budget audit() const noexcept
    {
        return (overruns_ > 0) ? Budget::DeadlineMiss : Budget::None;
    }

private:
    void commit(Clock::duration elapsed) noexcept;

    std::string_view          name_;
    std::chrono::microseconds deadline_;
    std::chrono::microseconds last_{0};
    std::chrono::microseconds worst_{0};
    std::chrono::microseconds total_{0};
    std::uint32_t             runs_{0};
    std::uint32_t             overruns_{0};
};

struct SectionAudit {
    Budget               flags{Budget::None};
    const SectionBudget* worst{nullptr}; // секція з найменшим запасом
};

[[nodiscard]] SectionAudit audit_sections(std::span<const SectionBudget> sections) noexcept;

} // namespace budget
