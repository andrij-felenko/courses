#include "load_profile.hpp"

#include <algorithm>

namespace autonomy {
namespace {

// Скільки штрафу Пейкерта знімає повний відпочинок комірки між імпульсами:
// за час сну іони встигають перерозподілитися по об'єму електроліту, і
// поверхневе виснаження електрода майже повністю розсмоктується.
constexpr double kRelaxCredit = 0.90;

double relaxed_cost(double raw_cost, Seconds rest, Seconds relax)
{
    if (raw_cost <= 1.0) {
        return 1.0;
    }
    if (relax <= Seconds{0}) {
        return raw_cost;
    }
    const double recovery = std::clamp(rest / relax, 0.0, 1.0);
    return 1.0 + (raw_cost - 1.0) * (1.0 - kRelaxCredit * recovery);
}

}  // namespace

std::expected<LoadProfile, Error> LoadProfile::create(Spec spec)
{
    if (spec.phases.empty()) {
        return std::unexpected{Error::NoPhases};
    }
    if (spec.period <= Seconds{0}) {
        return std::unexpected{Error::PeriodTooShort};
    }
    if (spec.sleep_current_ma < 0.0) {
        return std::unexpected{Error::NegativeCurrent};
    }
    for (const Phase& phase : spec.phases) {
        if (phase.duration <= std::chrono::milliseconds{0}) {
            return std::unexpected{Error::PhaseDurationNotPositive};
        }
        if (phase.current_ma < 0.0) {
            return std::unexpected{Error::NegativeCurrent};
        }
    }
    if (spec.depassivation) {
        if (spec.depassivation->duration <= std::chrono::milliseconds{0}) {
            return std::unexpected{Error::PhaseDurationNotPositive};
        }
        if (spec.depassivation->current_ma < 0.0) {
            return std::unexpected{Error::NegativeCurrent};
        }
        if (spec.depassivation_period <= Seconds{0}) {
            return std::unexpected{Error::PeriodTooShort};
        }
    }
    return LoadProfile{std::move(spec)};
}

std::expected<Load, Error> LoadProfile::analyse(const Cell& cell) const
{
    Load load;
    load.period = spec_.period;
    load.shares.reserve(spec_.phases.size() + 2);

    for (const Phase& phase : spec_.phases) {
        load.active += Seconds{phase.duration};
    }

    // Депасиваційний імпульс має власний, набагато довший період; у баланс
    // одного циклу він входить розмазаною часткою.
    double depass_scale = 0.0;
    Seconds depass_time{0};
    if (spec_.depassivation) {
        depass_scale = spec_.period / spec_.depassivation_period;
        depass_time = Seconds{spec_.depassivation->duration} * depass_scale;
    }

    load.rest = spec_.period - load.active - depass_time;
    if (load.rest < Seconds{0}) {
        return std::unexpected{Error::PeriodTooShort};  // не встигає заснути
    }

    double q_peukert = 0.0;

    for (const Phase& phase : spec_.phases) {
        const Seconds duration{phase.duration};
        const double charge = phase.current_ma * duration.count();  // Q = I · t
        const double cost = relaxed_cost(cell.peukert_cost(phase.current_ma), load.rest, cell.relax_time());

        load.q_active_mas += charge;
        q_peukert += charge * cost;
        load.shares.push_back({phase.name, phase.current_ma, duration, charge, 0.0, cost,
                               PhaseKind::Active});

        if (phase.current_ma > load.peak_current_ma) {
            load.peak_current_ma = phase.current_ma;
            load.peak_duration = duration;
            load.peak_phase = phase.name;
        }
    }

    const double q_sleep = spec_.sleep_current_ma * load.rest.count();
    q_peukert += q_sleep;  // мікроампери беруться нижче еталонного струму
    load.shares.push_back({"Глибокий сон", spec_.sleep_current_ma, load.rest, q_sleep, 0.0, 1.0,
                           PhaseKind::Sleep});

    double q_depass = 0.0;
    if (spec_.depassivation) {
        const Seconds duration{spec_.depassivation->duration};
        q_depass = spec_.depassivation->current_ma * duration.count() * depass_scale;
        const double cost = relaxed_cost(cell.peukert_cost(spec_.depassivation->current_ma),
                                         spec_.depassivation_period, cell.relax_time());
        q_peukert += q_depass * cost;
        load.shares.push_back({spec_.depassivation->name, spec_.depassivation->current_ma, duration,
                               q_depass, 0.0, cost, PhaseKind::Depassivation});
    }

    load.q_cycle_mas = load.q_active_mas + q_sleep + q_depass;
    load.q_cycle_peukert_mas = q_peukert;
    if (load.q_cycle_mas <= 0.0) {
        return std::unexpected{Error::NoDrain};
    }

    // η_pulse — у скільки разів імпульсний характер розряду знецінює паспортну
    // ємність: заряд, узятий струмом 45 мА, коштує дорожче за той самий заряд,
    // узятий мікроамперами.
    load.eta_pulse = load.q_cycle_mas / load.q_cycle_peukert_mas;
    load.i_avg_ma = load.q_cycle_mas / spec_.period.count();

    for (PhaseShare& share : load.shares) {
        share.share = share.charge_mas / load.q_cycle_mas;
    }
    return load;
}

}  // namespace autonomy
