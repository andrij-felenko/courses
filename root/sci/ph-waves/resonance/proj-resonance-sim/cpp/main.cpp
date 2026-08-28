#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <algorithm>
#include <span>

// Фізичні параметри осцилятора
struct OscillatorParams {
    double m{1.0};     // маса (кг)
    double k{100.0};   // жорсткість (Н/м)
    double c{1.0};     // демпфування (Н·с/м)
    double f0{10.0};   // амплітуда сили (Н)

    [[nodiscard]] constexpr double natural_frequency() const noexcept {
        return std::sqrt(k / m);
    }

    [[nodiscard]] constexpr double damping_rate() const noexcept {
        return c / (2.0 * m);
    }

    [[nodiscard]] constexpr double resonance_frequency() const noexcept {
        const double w0 = natural_frequency();
        const double g = damping_rate();
        const double val = w0 * w0 - 2.0 * g * g;
        return (val > 0.0) ? std::sqrt(val) : 0.0;
    }

    [[nodiscard]] constexpr double quality_factor() const noexcept {
        return natural_frequency() / (2.0 * damping_rate());
    }
};

// Точка профілю АЧХ
struct AFCPoint {
    double omega{0.0};
    double amplitude{0.0};
};

class DrivenOscillatorSimulator {
public:
    explicit DrivenOscillatorSimulator(OscillatorParams params)
        : params_(params) {}

    // Симуляція вимушених коливань на фіксованій частоті за методом Velocity Verlet
    [[nodiscard]] double simulate_frequency(double omega, double dt, double t_settle, double t_measure) const {
        double x = 0.0;
        double v = 0.0;
        double t = 0.0;

        auto compute_acc = [this](double x_pos, double v_vel, double f_ext) {
            return (f_ext - params_.c * v_vel - params_.k * x_pos) / params_.m;
        };

        double a = compute_acc(x, v, params_.f0);

        // Фаза 1: пропуск перехідного процесу
        while (t < t_settle) {
            const double f_next = params_.f0 * std::cos(omega * (t + dt));
            
            x += v * dt + 0.5 * a * dt * dt;
            const double a_next = compute_acc(x, v, f_next);
            v += 0.5 * (a + a_next) * dt;

            a = a_next;
            t += dt;
        }

        // Фаза 2: вимірювання максимуму амплітуди
        double max_amp = 0.0;
        const double t_end = t_settle + t_measure;

        while (t < t_end) {
            const double f_next = params_.f0 * std::cos(omega * (t + dt));

            x += v * dt + 0.5 * a * dt * dt;
            const double a_next = compute_acc(x, v, f_next);
            v += 0.5 * (a + a_next) * dt;

            a = a_next;
            t += dt;

            max_amp = std::max(max_amp, std::abs(x));
        }

        return max_amp;
    }

    // Сканування діапазону частот та повернення векторного профілю АЧХ
    [[nodiscard]] std::vector<AFCPoint> scan_afc(double w_min, double w_max, int steps, double dt) const {
        std::vector<AFCPoint> result;
        result.reserve(static_cast<size_t>(steps + 1));

        const double dw = (w_max - w_min) / steps;
        const double t_settle = 6.0 / params_.damping_rate(); // ~6 сталих часу 1/gamma
        const double t_measure = 10.0 * (2.0 * M_PI / params_.natural_frequency());

        for (int i = 0; i <= steps; ++i) {
            const double w = w_min + i * dw;
            const double amp = simulate_frequency(w, dt, t_settle, t_measure);
            result.push_back({w, amp});
        }

        return result;
    }

private:
    OscillatorParams params_;
};

int main() {
    const OscillatorParams params{.m = 1.0, .k = 100.0, .c = 1.0, .f0 = 10.0};
    const DrivenOscillatorSimulator sim(params);

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "=== ТЕОРЕТИЧНІ ПАРАМЕТРИ ===\n";
    std::cout << "Власна частота w0  : " << params.natural_frequency() << " рад/с\n";
    std::cout << "Резонансна частота : " << params.resonance_frequency() << " рад/с\n";
    std::cout << "Добротність Q      : " << params.quality_factor() << "\n\n";

    const auto afc = sim.scan_afc(5.0, 15.0, 100, 0.001);

    // Знаходимо резонансний пік через std::max_element
    const auto peak_it = std::max_element(
        afc.begin(), afc.end(),
        [](const AFCPoint& a, const AFCPoint& b) { return a.amplitude < b.amplitude; }
    );

    std::cout << "=== РЕЗУЛЬТАТИ СИМУЛЯЦІЇ ===\n";
    std::cout << "Знайдена резонансна частота : " << peak_it->omega << " рад/с\n";
    std::cout << "Максимальна амплітуда      : " << peak_it->amplitude << " м\n";
    
    const double a_stat = params.f0 / params.k;
    std::cout << "Коефіцієнт підсилення A/A_stat: " << (peak_it->amplitude / a_stat) << "\n";

    return 0;
}
