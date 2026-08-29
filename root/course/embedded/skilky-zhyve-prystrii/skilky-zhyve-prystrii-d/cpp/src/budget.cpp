#include "budget.hpp"

#include <algorithm>
#include <cmath>
#include <limits>

namespace autonomy {
namespace {

constexpr double kPlateauDepth = 0.50;    // «робоче плато» — напруга на половині розряду
constexpr double kEsrBudget    = 0.50;    // половину запасу напруги віддаємо на ESR буфера
constexpr double kHybridAbove  = 1.0e-3;  // більше за 1000 мкФ керамікою вже не набрати

// Скільки буферної ємності треба, щоб імпульс не просадив шину нижче порогу.
// Конденсатор рахуємо так, ніби комірка під час імпульсу не дає нічого: після
// місяців сну пасивована плівка саме так себе й поводить.
void size_buffer(const Cell& cell, const Site& site, const Load& load, PulseCheck& pulse)
{
    pulse.headroom_v = cell.ocv_at(kPlateauDepth) - site.cutoff_v;

    if (!pulse.brownout && !pulse.brownout_after_storage) {
        return;
    }

    const double pulse_a = load.peak_current_ma / 1000.0;
    if (pulse.headroom_v <= 0.0 || pulse_a <= 0.0) {
        // Поріг відсічки вищий за робоче плато комірки: тут не буфер треба, а
        // інша хімія, нижчий поріг або менший піковий струм.
        pulse.buffer_impossible = true;
        return;
    }

    const double usable_v = pulse.headroom_v * (1.0 - kEsrBudget);
    const double farads = pulse_a * load.peak_duration.count() / usable_v;  // C = I·t/ΔU
    pulse.buffer = Buffer{farads, pulse.headroom_v * kEsrBudget / pulse_a, farads > kHybridAbove};
}

PulseCheck check_pulse(const Cell& cell, const Site& site, const Load& load)
{
    PulseCheck pulse;
    const double pulse_a = load.peak_current_ma / 1000.0;

    pulse.r_int_ohm = cell.internal_resistance(site.temp_c);
    pulse.sag_v = pulse_a * pulse.r_int_ohm;
    pulse.v_term_v = cell.ocv_fresh_v() - pulse.sag_v;
    pulse.brownout = pulse.v_term_v < site.cutoff_v;

    pulse.r_passivated_ohm = pulse.r_int_ohm * cell.passivation_factor(site.storage);
    pulse.sag_storage_v = pulse_a * pulse.r_passivated_ohm;
    pulse.v_term_storage_v = cell.ocv_fresh_v() - pulse.sag_storage_v;
    pulse.brownout_after_storage = pulse.v_term_storage_v < site.cutoff_v;

    size_buffer(cell, site, load, pulse);
    return pulse;
}

void pick_limiter(Estimate& est)
{
    if (est.pulse.brownout) {
        est.limiter = Limiter::Brownout;
        est.limiter_note = "передавач валить шину нижче BOD ще на свіжій комірці";
        return;
    }
    if (est.i_self_ma > est.i_avg_ma) {
        est.limiter = Limiter::SelfDischarge;
        est.limiter_note = "оптимізувати прошивку далі немає сенсу";
        return;
    }

    const auto worst = std::ranges::max_element(est.load.shares, {}, &PhaseShare::charge_mas);
    if (worst != est.load.shares.end() && worst->kind == PhaseKind::Sleep) {
        est.limiter = Limiter::Sleep;
        est.limiter_note = "шукати паразитні витоки й струм спокою стабілізатора";
        return;
    }

    est.limiter = Limiter::ActivePhase;
    est.limiter_note = (worst != est.load.shares.end()) ? worst->name : std::string{"невідомо"};
}

}  // namespace

std::string_view describe(Limiter limiter) noexcept
{
    switch (limiter) {
    case Limiter::Brownout:      return "просадка напруги нижче порогу відсічки";
    case Limiter::SelfDischarge: return "саморозряд самої комірки";
    case Limiter::ActivePhase:   return "активна фаза пробудження";
    case Limiter::Sleep:         return "струм глибокого сну";
    }
    return "невідомо";
}

std::expected<Estimate, Error> estimate(const Cell& cell, const LoadProfile& profile, const Site& site)
{
    if (site.cutoff_v <= 0.0 || site.cutoff_v >= cell.ocv_fresh_v()) {
        return std::unexpected{Error::CutoffAboveFresh};
    }
    if (site.safety_factor <= 0.0 || site.safety_factor > 1.0) {
        return std::unexpected{Error::SafetyFactorOutOfRange};
    }

    auto load = profile.analyse(cell);
    if (!load) {
        return std::unexpected{load.error()};
    }

    Estimate est;
    est.load = *std::move(load);
    est.pulse = check_pulse(cell, site, est.load);

    // η_cutoff. Пристрій вимикається не тоді, коли OCV дійде до порогу, а тоді,
    // коли ПІД ІМПУЛЬСОМ напруга на клемах провалиться нижче нього. Тож поріг
    // на осі OCV піднятий на всю величину просадки.
    est.ocv_cutoff_v = site.cutoff_v + est.pulse.sag_v;
    est.eta_cutoff = cell.delivered_above(est.ocv_cutoff_v);
    est.eta_temp = cell.temperature_factor(site.temp_c);
    est.eta_pulse = est.load.eta_pulse;

    est.c_after_cutoff_mah = cell.capacity_mah() * est.eta_cutoff;
    est.c_after_temp_mah = est.c_after_cutoff_mah * est.eta_temp;
    est.c_eff_mah = est.c_after_temp_mah * est.eta_pulse;

    est.i_avg_ma = est.load.i_avg_ma;
    est.i_self_ma = cell.self_discharge_ma(site.temp_c);
    est.i_total_ma = est.i_avg_ma + est.i_self_ma;
    if (est.i_total_ma <= 0.0) {
        return std::unexpected{Error::NoDrain};
    }

    est.life = Hours{est.c_eff_mah / est.i_total_ma};
    est.life_years = est.life;
    est.guaranteed = est.life_years * site.safety_factor;

    // Наївна оцінка з початку статті: паспортна ємність поділена на середній
    // струм, без жодного коефіцієнта зниження.
    est.naive = Hours{cell.capacity_mah() / est.i_avg_ma};
    est.optimism_ratio = (est.life_years > Years{0}) ? est.naive / est.life_years
                                                     : std::numeric_limits<double>::infinity();

    pick_limiter(est);
    return est;
}

}  // namespace autonomy
