#pragma once

// Зведений аудит інженерних бюджетів під час роботи прошивки.
//
// Монітор нічого не вимірює сам: він дивиться на підсистеми через незмінні
// посилання й зшиває їхні показання в один вердикт і одну дію. Кожна
// підсистема лишається придатною до вжитку окремо від монітора.

#include "budget/energy_ledger.hpp"
#include "budget/flags.hpp"
#include "budget/flash_layout.hpp"
#include "budget/fragment_resource.hpp"
#include "budget/rail_monitor.hpp"
#include "budget/section_timer.hpp"
#include "budget/stack_guard.hpp"
#include "budget/thermal_model.hpp"

#include <chrono>
#include <cstddef>
#include <expected>
#include <span>
#include <string>

namespace budget {

class BudgetMonitor {
public:
    struct Limits {
        std::size_t        heap_min_free{8 * 1024};
        std::size_t        heap_min_largest{2 * 1024};
        double             battery_mah{2000.0};
        std::chrono::hours required_life{8760}; // рік автономності за ТЗ
    };

    struct Sources {
        std::span<const StackGuard>    stacks{};
        const FragmentAwareResource*   heap{nullptr};
        const RailMonitor*             rail{nullptr};
        const ThermalModel*            thermal{nullptr};
        const EnergyLedger*            energy{nullptr};
        std::span<const SectionBudget> sections{};
        FlashLayout                    flash{};
    };

    struct Report {
        Budget   flags{Budget::None};
        Severity severity{Severity::Ok};
        Action   action{Action::Run};

        StackAudit                       stacks{};
        FragmentAwareResource::Stats     heap{};
        std::expected<FlashPlan, Budget> flash{FlashPlan{}};

        double   rail_last_v{0.0};
        double   rail_min_v{0.0};
        double   rail_headroom_v{0.0};
        unsigned rail_sags{0};

        double ambient_c{0.0};
        double junction_c{0.0};
        double junction_peak_c{0.0};
        double thermal_headroom_w{0.0};

        Microamps          average_current{0};
        std::chrono::hours life{0};
        double             tx_charge_share{0.0};
        double             tx_time_share{0.0};

        std::string_view          worst_section{"—"};
        std::chrono::microseconds worst_section_time{0};
        std::chrono::microseconds worst_section_margin{0};
    };

    BudgetMonitor(Sources sources, Limits limits) noexcept
        : sources_{sources}, limits_{limits} {}

    [[nodiscard]] Report run() const;

private:
    Sources sources_;
    Limits  limits_;
};

[[nodiscard]] std::string to_text(const BudgetMonitor::Report& report);

} // namespace budget
