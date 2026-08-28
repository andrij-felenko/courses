#include <iostream>
#include <vector>
#include <cmath>
#include <span>
#include <expected>
#include <numeric>
#include <iomanip>

namespace physics {

/* Коди помилок та попереджень */
enum class SolverError {
    InvalidParam,
    MemoryAllocationFailed,
    NonlinearSaturation
};

/* Точкове джерело векторного або скалярного поля */
struct FieldSource {
    double x{0.0};
    double y{0.0};
    double charge{0.0};
};

/* Результат суперпозиції полів у точці */
struct FieldResult {
    double Ex{0.0};
    double Ey{0.0};
    double potential{0.0};
};

/* Обчислювач векторного поля на основі принципу суперпозиції */
class FieldSuperpositionSolver {
public:
    static std::expected<FieldResult, SolverError> 
    calculateAt(std::span<const FieldSource> sources, double px, double py) noexcept {
        if (sources.empty()) {
            return std::unexpected(SolverError::InvalidParam);
        }

        FieldResult res{};
        for (const auto& src : sources) {
            const double dx = px - src.x;
            const double dy = py - src.y;
            const double r2 = dx * dx + dy * dy;
            const double r = std::sqrt(std::max(r2, 1e-18));

            const double E_mag = src.charge / std::max(r2, 1e-18);
            res.Ex += E_mag * (dx / r);
            res.Ey += E_mag * (dy / r);
            res.potential += src.charge / r;
        }

        return res;
    }
};

/* Рушій часової суперпозиції (Згортка через імпульсну функцію Гріна) */
class GreenConvolutionEngine {
private:
    std::vector<double> h_;       // Імпульсний відгук G(t, t')
    double maxLinearAmp_{100.0};  // Межа лінійності

public:
    explicit GreenConvolutionEngine(std::vector<double> impulseResponse, double maxLinearAmp = 100.0)
        : h_(std::move(impulseResponse)), maxLinearAmp_(maxLinearAmp) {}

    [[nodiscard]] std::expected<std::vector<double>, SolverError>
    process(std::span<const double> input) const {
        if (input.empty() || h_.empty()) {
            return std::unexpected(SolverError::InvalidParam);
        }

        const size_t outLen = input.size() + h_.size() - 1;
        std::vector<double> output(outLen, 0.0);
        bool saturated = false;

        // Обчислення дискретної згортки: u[n] = ∑ₖ input[k] * h[n - k]
        for (size_t n = 0; n < outLen; ++n) {
            double sum = 0.0;
            for (size_t k = 0; k < input.size(); ++k) {
                if (n >= k && (n - k) < h_.size()) {
                    sum += input[k] * h_[n - k];
                }
            }
            output[n] = sum;
            if (std::abs(sum) > maxLinearAmp_) {
                saturated = true;
            }
        }

        return output;
    }

    [[nodiscard]] size_t impulseLength() const noexcept { return h_.size(); }
};

} // namespace physics

int main() {
    std::cout << "=== Симулятор суперпозиції (C++20 Implementation) ===\n\n";

    // 1. Суперпозиція кулонівських полів
    const std::vector<physics::FieldSource> sources{
        { .x = -2.0, .y = 0.0, .charge = 5.0 },
        { .x =  2.0, .y = 0.0, .charge = -3.0 },
        { .x =  0.0, .y = 3.0, .charge = 2.0 }
    };

    auto fieldRes = physics::FieldSuperpositionSolver::calculateAt(sources, 0.0, 0.0);
    if (fieldRes.has_value()) {
        std::cout << "[Електростатика C++] Поле у точці (0,0):\n"
                  << "  Ex        = " << std::setw(8) << std::fixed << std::setprecision(4) << fieldRes->Ex << " у.о.\n"
                  << "  Ey        = " << std::setw(8) << fieldRes->Ey << " у.о.\n"
                  << "  Потенціал = " << std::setw(8) << fieldRes->potential << " у.о.\n\n";
    }

    // 2. Згортка сигналів за допомогою імпульсної функції Гріна
    const std::vector<double> impulseResponse{ 1.0, 0.5, 0.25, 0.125, 0.0625 };
    const physics::GreenConvolutionEngine engine(impulseResponse, 10.0);

    const std::vector<double> inputSignal{ 1.0, 2.0, 1.5, 0.0, -1.0, 0.5, 0.0, 0.0 };
    auto convRes = engine.process(inputSignal);

    if (convRes.has_value()) {
        std::cout << "[DSP / Згортка C++] Результат суперпозиції y[n]:\n";
        for (size_t i = 0; i < convRes->size(); ++i) {
            std::cout << "  y[" << std::setw(2) << i << "] = "
                      << std::setw(7) << std::setprecision(4) << (*convRes)[i] << "\n";
        }
    }

    return 0;
}
