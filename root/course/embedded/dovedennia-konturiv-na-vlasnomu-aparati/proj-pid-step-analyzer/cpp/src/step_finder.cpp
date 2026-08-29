#include "step_finder.hpp"

#include <algorithm>
#include <cmath>
#include <optional>

namespace pid {
namespace {

Millis elapsed(const Sample& a, const Sample& b) noexcept {
    return std::chrono::duration_cast<Millis>(b.t - a.t);
}

/// Друга ступінь: 80 мс до фронту апарат має йти за завданням. Якщо він ще
/// дзвенить після попереднього фліпу, накладені коливання зіпсують і
/// перерегулювання, і час встановлення.
std::optional<std::size_t> quietBegin(std::span<const Sample> log, std::size_t edge,
                                      const DetectConfig& cfg) {
    std::size_t i = edge;
    while (i > 0 && elapsed(log[i - 1], log[edge]) <= cfg.quiet) --i;
    if (elapsed(log[i], log[edge]) < cfg.quiet * 0.9) return std::nullopt;  // історії немає

    const auto history = log.subspan(i, edge - i + 1);
    const bool disturbed = std::ranges::any_of(history, [&](const Sample& s) {
        return std::abs(s.setpoint - s.gyro) > cfg.quietErrMax;
    });
    return disturbed ? std::nullopt : std::optional{i};
}

/// Третя ступінь: завдання тримається щонайменше plateau. Вікно аналізу
/// тягнемо далі, до analysis, поки стік стоїть на місці.
std::optional<std::size_t> plateauEnd(std::span<const Sample> log, std::size_t edgeEnd,
                                      const DetectConfig& cfg) {
    const double level = log[edgeEnd].setpoint;
    std::size_t k = edgeEnd;
    while (k + 1 < log.size() && elapsed(log[edgeEnd], log[k + 1]) <= cfg.analysis) {
        if (std::abs(log[k + 1].setpoint - level) > cfg.plateauTol) break;
        ++k;
    }
    if (elapsed(log[edgeEnd], log[k]) < cfg.plateau * 0.95) return std::nullopt;
    return k;
}

Distortion scanDistortion(std::span<const Sample> window, const DetectConfig& cfg) {
    Distortion flags = Distortion::None;
    for (const auto& s : window) {
        if (std::abs(s.gyro) >= cfg.gyroClip) flags |= Distortion::GyroClip;
        if (s.vbat > 0.0 && s.vbat < cfg.vbatCutoff) flags |= Distortion::VbatSag;
    }
    return flags;
}

} // namespace

std::string describe(Distortion set) {
    std::string out;
    if (has(set, Distortion::GyroClip)) out += "кліпінг гіро";
    if (has(set, Distortion::VbatSag)) {
        if (!out.empty()) out += " + ";
        out += "просідання АКБ";
    }
    return out;
}

Search findSteps(std::span<const Sample> log, const DetectConfig& cfg) {
    Search result;
    if (log.size() < 3) return result;

    for (std::size_t i = 1; i + 1 < log.size(); ++i) {
        const double dt = secondsBetween(log[i - 1], log[i]);
        if (dt <= 0.0) continue;

        // Перша ступінь: фронт за швидкістю наростання завдання.
        const double slope = (log[i].setpoint - log[i - 1].setpoint) / dt;
        if (std::abs(slope) < cfg.edgeSlopeMin) continue;
        ++result.rejected.edges;

        const double dir = slope > 0.0 ? 1.0 : -1.0;
        const std::size_t begin = i - 1;
        std::size_t j = i;
        bool edgeDone = false;
        while (j + 1 < log.size()) {
            if ((log[j + 1].setpoint - log[j].setpoint) * dir <= 0.0) {
                edgeDone = true;                       // завдання зупинилось
                break;
            }
            if (elapsed(log[begin], log[j + 1]) > cfg.edgeMax) break;  // це плавний рух стіка
            ++j;
        }
        if (!edgeDone) {
            ++result.rejected.ramp;
            i = j;
            continue;
        }

        const double amplitude = log[j].setpoint - log[begin].setpoint;
        if (std::abs(amplitude) < cfg.edgeMinAmp) {
            ++result.rejected.small;
            i = j;
            continue;
        }
        const auto quiet = quietBegin(log, begin, cfg);
        if (!quiet) {
            ++result.rejected.noisy;
            i = j;
            continue;
        }
        const auto end = plateauEnd(log, j, cfg);
        if (!end) {
            ++result.rejected.noPlateau;
            i = j;
            continue;
        }

        StepWindow w;
        w.quietBegin = *quiet;
        w.begin = begin;
        w.edgeEnd = j;
        w.end = *end;
        w.amplitude = amplitude;
        w.distortion = scanDistortion(log.subspan(begin, *end - begin + 1), cfg);
        result.steps.push_back(w);

        i = *end;                                      // наступну шукаємо за вікном
    }

    return result;
}

} // namespace pid
