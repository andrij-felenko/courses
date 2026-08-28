#include <iostream>
#include <vector>
#include <cmath>
#include <optional>
#include <span>
#include <numbers>
#include <iomanip>

struct SweepPoint {
    double freq_hz{0.0};
    double magnitude{0.0};
};

struct QFactorResult {
    double f0_hz{0.0};
    double bw_3db_hz{0.0};
    double q_loaded{0.0};
    double q_unloaded{0.0};
    double esr_ohm{0.0};
    double inductance_h{0.0};
};

class QMeterDSP {
public:
    [[nodiscard]] static std::optional<QFactorResult> calculate(
        std::span<const SweepPoint> sweep,
        double z_system = 50.0) noexcept
    {
        if (sweep.size() < 5) {
            return std::nullopt;
        }

        // 1. Пошук грубого дискретного піка
        size_t k = 0;
        double max_val = sweep[0].magnitude;
        for (size_t i = 1; i < sweep.size(); ++i) {
            if (sweep[i].magnitude > max_val) {
                max_val = sweep[i].magnitude;
                k = i;
            }
        }

        if (k == 0 || k == sweep.size() - 1) {
            return std::nullopt;
        }

        // 2. Параболічна інтерполяція вершини
        const double y1 = sweep[k - 1].magnitude;
        const double y2 = sweep[k].magnitude;
        const double y3 = sweep[k + 1].magnitude;

        const double denom = y1 - 2.0 * y2 + y3;
        if (std::abs(denom) < 1e-15) {
            return std::nullopt;
        }

        const double delta = 0.5 * (y1 - y3) / denom;
        const double df = sweep[k].freq_hz - sweep[k - 1].freq_hz;
        const double f0 = sweep[k].freq_hz + delta * df;
        const double peak_mag = y2 - 0.25 * (y1 - y3) * delta;

        // 3. Рівень -3 дБ
        constexpr double inv_sqrt2 = 0.7071067811865475;
        const double target_3db = peak_mag * inv_sqrt2;

        // Пошук лівої точки f_low
        std::optional<double> f_low;
        for (size_t i = k; i > 0; --i) {
            if (sweep[i - 1].magnitude <= target_3db && sweep[i].magnitude >= target_3db) {
                const double dy = sweep[i].magnitude - sweep[i - 1].magnitude;
                if (std::abs(dy) > 1e-15) {
                    const double frac = (target_3db - sweep[i - 1].magnitude) / dy;
                    f_low = sweep[i - 1].freq_hz + frac * (sweep[i].freq_hz - sweep[i - 1].freq_hz);
                    break;
                }
            }
        }

        // Пошук правої точки f_high
        std::optional<double> f_high;
        for (size_t i = k; i < sweep.size() - 1; ++i) {
            if (sweep[i].magnitude >= target_3db && sweep[i + 1].magnitude <= target_3db) {
                const double dy = sweep[i].magnitude - sweep[i + 1].magnitude;
                if (std::abs(dy) > 1e-15) {
                    const double frac = (sweep[i].magnitude - target_3db) / dy;
                    f_high = sweep[i].freq_hz + frac * (sweep[i + 1].freq_hz - sweep[i].freq_hz);
                    break;
                }
            }
        }

        if (!f_low || !f_high || *f_high <= *f_low) {
            return std::nullopt;
        }

        // 4. Розрахунок підсумкових параметрів
        QFactorResult res;
        res.f0_hz = f0;
        res.bw_3db_hz = *f_high - *f_low;
        res.q_loaded = res.f0_hz / res.bw_3db_hz;

        const double t0 = std::min(peak_mag, 1.0);
        if (t0 > 0.001) {
            res.q_unloaded = res.q_loaded / (1.0 - t0);
            res.esr_ohm = (2.0 * z_system) * (1.0 - t0) / t0;
        } else {
            res.q_unloaded = res.q_loaded;
            res.esr_ohm = 2.0 * z_system;
        }

        const double omega0 = 2.0 * std::numbers::pi * res.f0_hz;
        res.inductance_h = (res.q_unloaded * res.esr_ohm) / omega0;

        return res;
    }
};

int main() {
    const std::vector<SweepPoint> data = {
        { 9.6e6, 0.120 },
        { 9.7e6, 0.220 },
        { 9.8e6, 0.450 },
        { 9.9e6, 0.780 },
        { 10.0e6, 0.940 },
        { 10.1e6, 0.810 },
        { 10.2e6, 0.480 },
        { 10.3e6, 0.240 },
        { 10.4e6, 0.130 }
    };

    if (const auto res = QMeterDSP::calculate(data, 50.0)) {
        std::cout << std::fixed << std::setprecision(3);
        std::cout << "Резонансна частота f0 : " << res->f0_hz / 1e6 << " МГц\n";
        std::cout << "Смуга пропускання BW  : " << res->bw_3db_hz / 1e3 << " кГц\n";
        std::cout << "Навантажена Q_L       : " << res->q_loaded << "\n";
        std::cout << "Власна добротність Q0 : " << res->q_unloaded << "\n";
        std::cout << "Втрати котушки ESR    : " << res->esr_ohm << " Ом\n";
        std::cout << "Індуктивність L       : " << res->inductance_h * 1e6 << " мкГн\n";
    } else {
        std::cerr << "Помилка розрахунку добротності.\n";
    }

    return 0;
}
