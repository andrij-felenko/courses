#include "step_metrics.hpp"

#include <algorithm>
#include <cmath>
#include <numbers>
#include <vector>

namespace pid {
namespace {

constexpr double kNoiseCutoffHz = 30.0;    ///< усе, що вище, вважаємо шумом D-терма
constexpr Millis kPlateauSkip{50.0};       ///< перші 50 мс плато ще зайняті перехідним процесом
constexpr std::size_t kMinNoiseSamples = 16;

double clamp01(double v) noexcept { return std::clamp(v, 0.0, 1.0); }

Millis elapsed(const Sample& a, const Sample& b) noexcept {
    return std::chrono::duration_cast<Millis>(b.t - a.t);
}

/// Мить перетину рівня, лінійно між сусідніми відліками: на 8 кГц лозі крок
/// 125 мкс, і без інтерполяції час наростання квантується так грубо, що
/// різниця між добрим і перетюненим контуром губиться.
std::optional<Micros> crossingTime(std::span<const Sample> log, std::size_t from, std::size_t to,
                                   double level, double dir) {
    for (std::size_t i = from + 1; i <= to; ++i) {
        const double prev = log[i - 1].gyro;
        const double cur = log[i].gyro;
        if ((cur - level) * dir >= 0.0 && (prev - level) * dir < 0.0) {
            const double span = cur - prev;
            const double frac = (span != 0.0) ? clamp01((level - prev) / span) : 0.0;
            const auto step = Micros{static_cast<double>((log[i].t - log[i - 1].t).count())};
            return Micros{static_cast<double>(log[i - 1].t.count())} + step * frac;
        }
    }
    return std::nullopt;
}

/// Шум D-терма: однополюсний ФНЧ дає «повільну» складову d_filtered, а нас
/// цікавить середньоквадратичний залишок d_out − d_filtered — саме та
/// потужність, що гріє мідь статора, не рухаючи апарата.
std::optional<double> dTermNoise(std::span<const Sample> log, const StepWindow& w) {
    std::size_t p = w.edgeEnd;
    while (p < w.end && elapsed(log[w.edgeEnd], log[p]) < kPlateauSkip) ++p;
    if (w.end < p + kMinNoiseSamples) return std::nullopt;

    const double rc = 1.0 / (2.0 * std::numbers::pi * kNoiseCutoffHz);
    double filtered = log[p].dTerm;
    double sumSq = 0.0;
    std::size_t n = 0;
    for (std::size_t i = p + 1; i <= w.end; ++i) {
        const double dt = secondsBetween(log[i - 1], log[i]);
        const double alpha = std::min(1.0, dt / (dt + rc));
        filtered += alpha * (log[i].dTerm - filtered);
        const double residual = log[i].dTerm - filtered;
        sumSq += residual * residual;
        ++n;
    }
    return std::sqrt(sumSq / static_cast<double>(n));
}

int countRinging(std::span<const Sample> log, const StepWindow& w, std::size_t peakIdx,
                 double target, double deadband) {
    int crossings = 0;
    int lastSign = 0;
    for (std::size_t i = peakIdx; i <= w.end; ++i) {
        const double e = log[i].gyro - target;
        if (std::abs(e) < deadband) continue;   // інакше шум дав би десятки «перетинів»
        const int sign = e > 0.0 ? 1 : -1;
        if (lastSign != 0 && sign != lastSign) ++crossings;
        lastSign = sign;
    }
    return crossings;
}

double medianOf(std::vector<double> v) {
    std::ranges::sort(v);
    const std::size_t n = v.size();
    return (n % 2 == 1) ? v[n / 2] : 0.5 * (v[n / 2 - 1] + v[n / 2]);
}

} // namespace

std::optional<StepMetrics> measure(std::span<const Sample> log, const StepWindow& w) {
    if (w.end <= w.edgeEnd || w.end - w.begin < 8) return std::nullopt;

    // Базова лінія — середнє гіро на спокійній передісторії, а не один відлік:
    // окремий відлік містить і турбулентність, і шум давача.
    const auto history = log.subspan(w.quietBegin, w.begin - w.quietBegin + 1);
    double base = 0.0;
    for (const auto& s : history) base += s.gyro;
    base /= static_cast<double>(history.size());

    const double target = log[w.edgeEnd].setpoint;
    const double amplitude = target - base;
    if (std::abs(amplitude) < 1e-6) return std::nullopt;
    const double dir = amplitude > 0.0 ? 1.0 : -1.0;

    const auto start = Micros{static_cast<double>(log[w.begin].t.count())};
    const auto t5 = crossingTime(log, w.begin, w.end, base + 0.05 * amplitude, dir);
    if (!t5) return std::nullopt;                       // реакції немає — міряти нічого

    StepMetrics m;
    m.amplitude = amplitude;
    m.tau = std::chrono::duration_cast<Millis>(*t5 - start);

    const auto t10 = crossingTime(log, w.begin, w.end, base + 0.10 * amplitude, dir);
    const auto t90 = crossingTime(log, w.begin, w.end, base + 0.90 * amplitude, dir);
    if (t10 && t90 && *t90 > *t10) {
        m.riseTime = std::chrono::duration_cast<Millis>(*t90 - *t10);
    }

    // Перший екстремум після фронту. Ділимо на амплітуду сходинки, а не на
    // абсолютне завдання: маневр із ненульової кутової швидкості інакше дав би
    // нісенітницю, а біля завдання ≈ 0 — ділення на нуль.
    const auto tail = log.subspan(w.edgeEnd, w.end - w.edgeEnd + 1);
    const auto peak = std::ranges::max_element(tail, {}, [&](const Sample& s) {
        return (s.gyro - target) * dir;
    });
    const double peakExcess = (peak->gyro - target) * dir;
    m.overshootPct = peakExcess > 0.0 ? peakExcess / std::abs(amplitude) * 100.0 : 0.0;
    const auto peakIdx = w.edgeEnd + static_cast<std::size_t>(peak - tail.begin());

    // Час встановлення — від останнього виходу з коридору ±5%, а не від першого входу.
    const double band = 0.05 * std::abs(amplitude);
    std::optional<std::size_t> lastOut;
    for (std::size_t i = w.begin; i <= w.end; ++i) {
        if (std::abs(log[i].gyro - target) > band) lastOut = i;
    }
    if (!lastOut) {
        m.settlingTime = Millis{0.0};
        m.settled = true;
    } else if (*lastOut == w.end) {
        m.settlingTime = elapsed(log[w.begin], log[w.end]);   // нижня оцінка: не заспокоївся
        m.settled = false;
    } else {
        const double a = log[*lastOut].gyro;
        const double b = log[*lastOut + 1].gyro;
        const double edge = target + (a > target ? band : -band);
        const double frac = (b != a) ? clamp01((edge - a) / (b - a)) : 1.0;
        const auto step = Micros{static_cast<double>((log[*lastOut + 1].t - log[*lastOut].t).count())};
        const auto crossed = Micros{static_cast<double>(log[*lastOut].t.count())} + step * frac;
        m.settlingTime = std::chrono::duration_cast<Millis>(crossed - start);
        m.settled = true;
    }

    m.ringCrossings = countRinging(log, w, peakIdx, target, 0.02 * std::abs(amplitude));
    m.dNoiseRms = dTermNoise(log, w);
    return m;
}

StepMetrics median(std::span<const StepMetrics> series) {
    StepMetrics out;
    if (series.empty()) return out;

    const auto collect = [&](auto&& pick) {
        std::vector<double> v;
        v.reserve(series.size());
        for (const auto& m : series) {
            if (const auto value = pick(m)) v.push_back(*value);
        }
        return v;
    };

    out.amplitude = medianOf(collect([](const StepMetrics& m) { return std::optional{m.amplitude}; }));
    out.tau = Millis{medianOf(collect([](const StepMetrics& m) { return std::optional{m.tau.count()}; }))};
    out.overshootPct =
        medianOf(collect([](const StepMetrics& m) { return std::optional{m.overshootPct}; }));
    out.settlingTime =
        Millis{medianOf(collect([](const StepMetrics& m) { return std::optional{m.settlingTime.count()}; }))};
    out.ringCrossings = static_cast<int>(std::lround(
        medianOf(collect([](const StepMetrics& m) { return std::optional{static_cast<double>(m.ringCrossings)}; }))));

    // Час наростання беремо лише зі сходинок, що справді дійшли до 90%,
    // шум — лише з тих, де плато вистачило на оцінку.
    if (auto rise = collect([](const StepMetrics& m) {
            return m.riseTime ? std::optional<double>{m.riseTime->count()} : std::optional<double>{};
        });
        !rise.empty()) {
        out.riseTime = Millis{medianOf(std::move(rise))};
    }
    if (auto noise = collect([](const StepMetrics& m) { return m.dNoiseRms; }); !noise.empty()) {
        out.dNoiseRms = medianOf(std::move(noise));
    }
    out.settled = std::ranges::all_of(series, [](const StepMetrics& m) { return m.settled; });
    return out;
}

} // namespace pid
