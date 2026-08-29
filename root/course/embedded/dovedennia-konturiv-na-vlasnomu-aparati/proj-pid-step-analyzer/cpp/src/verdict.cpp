#include "verdict.hpp"

namespace pid {
namespace {

// Пороги відкалібровані для квадрокоптерів 5–10 дюймів на 4S–6S.
constexpr double kTauLaggyMs = 24.0;
constexpr double kRiseSlowMs = 90.0;
constexpr double kRiseTwitchyMs = 20.0;
constexpr double kOvershootHighPct = 22.0;
constexpr double kOvershootFlatPct = 1.0;
constexpr double kNoiseWatch = 15.0;
constexpr double kNoiseHot = 35.0;
constexpr int kRingMany = 4;

} // namespace

Bands classify(const StepMetrics& m) {
    Bands b;
    b.tau = m.tau.count() > kTauLaggyMs ? Band::Undertuned : Band::Healthy;

    if (!m.riseTime) {
        b.rise = Band::Undertuned;                       // до 90% так і не дотягнув
    } else if (m.riseTime->count() > kRiseSlowMs) {
        b.rise = Band::Undertuned;
    } else if (m.riseTime->count() < kRiseTwitchyMs) {
        b.rise = Band::Overtuned;
    } else {
        b.rise = Band::Healthy;
    }

    if (m.overshootPct > kOvershootHighPct) {
        b.overshoot = Band::Overtuned;
    } else if (m.overshootPct < kOvershootFlatPct) {
        b.overshoot = Band::Undertuned;
    } else {
        b.overshoot = Band::Healthy;
    }

    if (!m.dNoiseRms) {
        b.noise = Band::Unknown;
    } else if (*m.dNoiseRms > kNoiseHot) {
        b.noise = Band::Overtuned;
    } else if (*m.dNoiseRms > kNoiseWatch) {
        b.noise = Band::Watch;
    } else {
        b.noise = Band::Healthy;
    }

    return b;
}

Tune judge(const StepMetrics& m, const Bands& b) {
    // Порядок не довільний: поки затримка завелика, крутити P і D безглуздо —
    // жорсткіший контур просто швидше зірветься.
    if (b.tau == Band::Undertuned) return Tune::SystemLaggy;
    if (b.noise == Band::Overtuned) return Tune::DNoise;
    if (b.overshoot == Band::Overtuned) {
        return m.ringCrossings > kRingMany ? Tune::PHigh : Tune::DLow;
    }
    if (!m.settled) return Tune::NotSettled;
    if (b.rise == Band::Overtuned) return Tune::RiseTooFast;
    if (b.rise == Band::Undertuned && b.overshoot == Band::Undertuned) return Tune::PLow;
    if (b.overshoot == Band::Undertuned) return Tune::Overdamped;
    return Tune::Healthy;
}

Advice adviceFor(Tune t) {
    switch (t) {
    case Tune::Healthy:
        return {"контур збалансовано", "лишити як є; повторити заміри на розрядженій батареї"};
    case Tune::SystemLaggy:
        return {"система млява: завелике транспортне запізнення",
                "розширити смугу фільтрів гіроскопа або перейти на швидший протокол ESC "
                "(DShot600); нарощувати P і D зараз шкідливо"};
    case Tune::DNoise:
        return {"ВЧ-шум D-терма: мотори гріються даремно",
                "зменшити K_d на 20% або увімкнути динамічний режекторний фільтр за обертами"};
    case Tune::PHigh:
        return {"завеликий P: дзвін навколо завдання", "зменшити P на 15%: контур розгойдує сам себе"};
    case Tune::DLow:
        return {"замалий D: одиничний відскок без демпфування",
                "збільшити D на 10–15%: наростання швидке, бракує саме демпфування"};
    case Tune::RiseTooFast:
        return {"надто різке наростання: ризик самозбудження",
                "зменшити P на 10%: на просілій батареї такий контур зірветься"};
    case Tune::PLow:
        return {"замалий P: ватне керування", "збільшити P на 15–20%: апарат не встигає за завданням"};
    case Tune::Overdamped:
        return {"передемпфована реакція", "зменшити D на 10% або підняти P: реакція надто в'язка"};
    case Tune::NotSettled:
        return {"апарат не заспокоївся до кінця вікна",
                "подовжити маневр у тесті або шукати механічний резонанс: коливання не згасають"};
    }
    return {"невідомо", ""};
}

std::string_view name(Band b) {
    switch (b) {
    case Band::Healthy:    return "норма";
    case Band::Watch:      return "пильнуй";
    case Band::Undertuned: return "замало";
    case Band::Overtuned:  return "забагато";
    case Band::Unknown:    return "н/д";
    }
    return "н/д";
}

} // namespace pid
