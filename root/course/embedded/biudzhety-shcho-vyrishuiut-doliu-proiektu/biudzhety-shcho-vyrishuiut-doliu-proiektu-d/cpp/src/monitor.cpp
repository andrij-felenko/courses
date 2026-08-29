#include "budget/monitor.hpp"

#include <algorithm>
#include <format>

namespace budget {

BudgetMonitor::Report BudgetMonitor::run() const
{
    Report report;

    // 1. Пам'ять: стеки задач, куча та розкладка Flash під OTA.
    report.stacks = audit_stacks(sources_.stacks);
    report.flags |= report.stacks.flags;

    if (sources_.heap != nullptr) {
        report.heap = sources_.heap->stats();
        report.flags |= sources_.heap->audit(limits_.heap_min_free,
                                             limits_.heap_min_largest);
    }

    report.flash = plan_flash(sources_.flash);
    if (report.flash.has_value()) {
        if (report.flash->tight) {
            report.flags |= Budget::FlashTight;
        }
    } else {
        report.flags |= report.flash.error();
    }

    // 2. Живлення: найгірший відлік шини важить більше за поточний.
    if (sources_.rail != nullptr) {
        const RailMonitor& rail = *sources_.rail;

        report.rail_last_v     = rail.last_v();
        report.rail_min_v      = rail.min_v();
        report.rail_headroom_v = rail.headroom_v();
        report.rail_sags       = rail.sags();

        if (rail.brownouts() > 0) {
            report.flags |= Budget::RailBrownout | Budget::RailSag;
        } else if (rail.sags() > 0) {
            report.flags |= Budget::RailSag;
        }
    }

    // 3. Тепло: судимо за піковою температурою кристала, а не за поточною.
    if (sources_.thermal != nullptr) {
        const ThermalModel& thermal = *sources_.thermal;

        report.ambient_c        = thermal.ambient_c();
        report.junction_c       = thermal.junction_c();
        report.junction_peak_c  = thermal.peak_c();
        report.thermal_headroom_w =
            std::max(0.0, thermal.max_power(thermal.ambient_c()) - thermal.power_w());

        if (thermal.trips() > 0 || thermal.peak_c() >= thermal.limits().tj_max_c) {
            report.flags |= Budget::ThermalTrip | Budget::ThermalWarning;
        } else if (thermal.peak_c() >= thermal.warn_threshold_c()) {
            report.flags |= Budget::ThermalWarning;
        }
    }

    // 4. Енергія: середній струм проти заявленого ресурсу автономності.
    if (sources_.energy != nullptr) {
        const EnergyLedger& energy = *sources_.energy;

        report.average_current = energy.average_current();
        report.life            = energy.predicted_life(limits_.battery_mah);
        report.tx_charge_share = energy.charge_share(Phase::Transmit);
        report.tx_time_share   = energy.time_share(Phase::Transmit);

        report.flags |= energy.audit(limits_.battery_mah, limits_.required_life);
    }

    // 5. Час: найтісніша критична секція.
    const SectionAudit sections = audit_sections(sources_.sections);
    report.flags |= sections.flags;
    if (sections.worst != nullptr) {
        report.worst_section        = sections.worst->name();
        report.worst_section_time   = sections.worst->worst();
        report.worst_section_margin = sections.worst->margin();
    }

    report.severity = severity(report.flags);
    report.action   = action(report.flags);
    return report;
}

std::string to_text(const BudgetMonitor::Report& report)
{
    std::string text = std::format("АУДИТ БЮДЖЕТІВ: {}\n  дія: {}\n\n",
                                   describe(report.flags),
                                   describe(report.action));

    text += std::format("  стеки: найтісніша задача «{}», запас {} Б\n",
                        report.stacks.worst_name, report.stacks.worst_free);

    text += std::format(
        "  куча:  вільно {} Б, найбільший блок {} Б, розривів {}, "
        "фрагментація {:.1f} %, відмов {}\n",
        report.heap.free_total, report.heap.largest_free, report.heap.free_blocks,
        report.heap.fragmentation * 100.0, report.heap.failures);

    if (report.flash.has_value()) {
        const FlashPlan& plan = *report.flash;
        text += std::format(
            "  flash: слот {} Б, запас у слоті {} Б, образ {:.1f} % обсягу, "
            "поза слотами {} Б, OTA можливий\n",
            plan.slot_bytes, plan.slot_free_bytes, plan.image_share * 100.0,
            plan.unusable_bytes);
    } else {
        text += std::format("  flash: OTA НЕМОЖЛИВИЙ ({})\n",
                            describe(report.flash.error()));
    }

    text += std::format(
        "  шина:  поточна {:.3f} В, мінімум {:.3f} В, запас до BOR {:.3f} В, "
        "просідань {}\n",
        report.rail_last_v, report.rail_min_v, report.rail_headroom_v,
        report.rail_sags);

    text += std::format(
        "  тепло: середовище {:.1f} °C, кристал {:.1f} °C, пік {:.1f} °C, "
        "запас потужності {:.3f} Вт\n",
        report.ambient_c, report.junction_c, report.junction_peak_c,
        report.thermal_headroom_w);

    if (report.life == std::chrono::hours::max()) {
        text += std::format(
            "  струм: середній {} мкА, ресурс поза роздільністю обліку\n",
            report.average_current);
    } else {
        text += std::format(
            "  струм: середній {} мкА, ресурс {} год ({} діб), "
            "передавач: {:.2f} % часу й {:.1f} % заряду\n",
            report.average_current, report.life.count(),
            report.life.count() / 24, report.tx_time_share * 100.0,
            report.tx_charge_share * 100.0);
    }

    text += std::format(
        "  час:   найтісніша секція «{}», найгірше {} мкс, запас {} мкс\n",
        report.worst_section, report.worst_section_time.count(),
        report.worst_section_margin.count());

    return text;
}

} // namespace budget
