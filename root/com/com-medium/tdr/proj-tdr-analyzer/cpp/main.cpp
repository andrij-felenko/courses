#include <vector>
#include <cmath>
#include <optional>
#include <stdexcept>
#include <string_view>
#include <algorithm>
#include <span>
#include <numeric>

enum class FaultType {
    None,
    ShortCircuit,
    OpenCircuit,
    HighImpedance,
    LowImpedance,
    CapacitiveDip,
    InductivePeak
};

struct TdrEvent {
    double distance_m{0.0};
    double time_ns{0.0};
    double gamma{0.0};
    double impedance_ohm{0.0};
    FaultType type{FaultType::None};
};

struct TdrAnalysisResult {
    std::vector<double> distances_m;
    std::vector<double> impedances_ohm;
    std::vector<TdrEvent> detected_events;
};

class TdrAnalyzer {
public:
    static constexpr double SpeedOfLight = 299792458.0;

    static TdrAnalysisResult process(std::span<const double> raw_voltage,
                                     double dt_sec,
                                     double z0_ohm = 50.0,
                                     double er_relative = 2.25) {
        if (raw_voltage.size() < 20) {
            throw std::invalid_argument("Масив відліків занадто малий для аналізу (мінімум 20)");
        }
        if (dt_sec <= 0.0 || z0_ohm <= 0.0 || er_relative < 1.0) {
            throw std::invalid_argument("Некоректні фізичні параметри лінії");
        }

        // 1. Фільтрація шуму ковзним середнім (вікно = 5 відліків)
        std::vector<double> v_smooth(raw_voltage.size());
        for (size_t i = 0; i < raw_voltage.size(); ++i) {
            double sum = 0.0;
            size_t count = 0;
            for (int k = -2; k <= 2; ++k) {
                ssize_t idx = static_cast<ssize_t>(i) + k;
                if (idx >= 0 && idx < static_cast<ssize_t>(raw_voltage.size())) {
                    sum += raw_voltage[idx];
                    count++;
                }
            }
            v_smooth[i] = sum / static_cast<double>(count);
        }

        // 2. Оцінка рівня базової лінії V_base
        const double v_base = std::accumulate(v_smooth.begin(), v_smooth.begin() + 10, 0.0) / 10.0;

        // 3. Пошук максимуму перепаду
        const double v_max = *std::max_element(v_smooth.begin(), v_smooth.end());
        const double v_inc = v_max - v_base;
        if (v_inc < 1e-4) {
            throw std::runtime_error("Падаючий перепад напруги не виявлено у масиві");
        }

        // 4. Детектування фронту t0 із субдискретною інтерполяцією
        const double v_thresh = v_base + 0.5 * v_inc;
        double t0_idx = -1.0;

        for (size_t i = 0; i < v_smooth.size() - 1; ++i) {
            if (v_smooth[i] <= v_thresh && v_smooth[i + 1] > v_thresh) {
                const double dy = v_smooth[i + 1] - v_smooth[i];
                const double fraction = (dy > 1e-9) ? ((v_thresh - v_smooth[i]) / dy) : 0.0;
                t0_idx = static_cast<double>(i) + fraction;
                break;
            }
        }

        if (t0_idx < 0.0) {
            throw std::runtime_error("Фронт наростання перепаду не перетинає рівень 50%");
        }

        TdrAnalysisResult result;
        result.distances_m.resize(v_smooth.size());
        result.impedances_ohm.resize(v_smooth.size());

        const double v_prop = SpeedOfLight / std::sqrt(er_relative);

        // 5. Розрахунок профілю відстаней та опорів
        for (size_t i = 0; i < v_smooth.size(); ++i) {
            const double dt = (static_cast<double>(i) - t0_idx) * dt_sec;
            result.distances_m[i] = (dt > 0.0) ? (v_prop * dt / 2.0) : 0.0;

            double gamma = (v_smooth[i] - (v_base + v_inc)) / v_inc;
            gamma = std::clamp(gamma, -0.999, 0.999);

            result.impedances_ohm[i] = z0_ohm * (1.0 + gamma) / (1.0 - gamma);
        }

        // 6. Виявлення подій (Event Detector)
        const size_t start_idx = static_cast<size_t>(t0_idx) + 5;
        for (size_t i = start_idx; i < v_smooth.size() - 1; ++i) {
            const double gamma = (v_smooth[i] - (v_base + v_inc)) / v_inc;

            if (std::abs(gamma) > 0.12) {
                // Перевірка умови локального екстремуму
                if ((v_smooth[i] >= v_smooth[i - 1] && v_smooth[i] >= v_smooth[i + 1]) ||
                    (v_smooth[i] <= v_smooth[i - 1] && v_smooth[i] <= v_smooth[i + 1])) {

                    TdrEvent ev;
                    ev.distance_m = result.distances_m[i];
                    ev.time_ns = (static_cast<double>(i) - t0_idx) * dt_sec * 1e9;
                    ev.gamma = gamma;
                    ev.impedance_ohm = result.impedances_ohm[i];

                    if (gamma > 0.85) ev.type = FaultType::OpenCircuit;
                    else if (gamma < -0.85) ev.type = FaultType::ShortCircuit;
                    else if (gamma > 0.15) ev.type = FaultType::HighImpedance;
                    else if (gamma < -0.15) ev.type = FaultType::LowImpedance;

                    result.detected_events.push_back(ev);
                    i += 3; // Антидребезговий зсув
                }
            }
        }

        return result;
    }
};
