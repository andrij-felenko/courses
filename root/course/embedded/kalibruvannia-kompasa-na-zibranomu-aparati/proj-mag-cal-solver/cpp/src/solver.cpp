// ===========================================================================
//  solver.cpp — Левенберг — Марквардт на дев'ять параметрів
//
//      p = [ V0x, V0y, V0z, W11, W12, W13, W22, W23, W33 ]
//      r_i = ‖ W · (B_i − V0) ‖ − B_earth
//
//  W тримається симетричною за побудовою: несиметрична частина — це поворот,
//  а поворот сенсора вже враховано монтажною матрицею плати.
// ===========================================================================

#include "mag_cal/solver.hpp"

#include <algorithm>
#include <array>
#include <cmath>

#include "mag_cal/linear_solver.hpp"

namespace mag_cal {
namespace {

constexpr std::size_t kParams = 9;
constexpr int kMaxIterations = 20;
constexpr int kMaxDampingTries = 8;
constexpr float kLambdaStart = 1e-3F;
constexpr float kLambdaMax = 1e9F;
constexpr float kLambdaMin = 1e-9F;

using ParamVector = std::array<float, kParams>;
using NormalMatrix = std::array<ParamVector, kParams>;

[[nodiscard]] Mat3 matrix_of(const ParamVector& p) noexcept {
    return Mat3::symmetric(p[3], p[4], p[5], p[6], p[7], p[8]);
}

[[nodiscard]] Vec3 offset_of(const ParamVector& p) noexcept {
    return {p[0], p[1], p[2]};
}

// Параметри не мають права тікати в нефізичну область: зміщення понад
// півтори тисячі мкТл означає вироджену хмару, а не стільки заліза на борту.
[[nodiscard]] bool plausible(const ParamVector& p) noexcept {
    if (!std::ranges::all_of(p, [](float v) { return std::isfinite(v); })) {
        return false;
    }
    if (std::abs(p[0]) > limits::kMaxOffsetUt || std::abs(p[1]) > limits::kMaxOffsetUt ||
        std::abs(p[2]) > limits::kMaxOffsetUt) {
        return false;
    }
    return std::all_of(p.begin() + 3, p.end(),
                       [](float v) { return std::abs(v) <= limits::kMaxGain; });
}

[[nodiscard]] float cost_of(std::span<const Vec3> samples, const ParamVector& p,
                            float earth_b) noexcept {
    const Mat3 w = matrix_of(p);
    const Vec3 v0 = offset_of(p);

    float sum_sq = 0.0F;
    for (const Vec3& raw : samples) {
        const float residual = (w * (raw - v0)).norm() - earth_b;
        sum_sq += residual * residual;
    }
    return sum_sq;
}

// H = JᵀJ і g = Jᵀr за один прохід. Повний гессіан не рахуємо: наближення
// Гаусса — Ньютона стійкіше на шумних даних, ніж друга похідна.
struct NormalEquations {
    NormalMatrix hessian{};
    ParamVector gradient{};
    float cost{0.0F};
};

[[nodiscard]] NormalEquations accumulate(std::span<const Vec3> samples,
                                         const ParamVector& p,
                                         float earth_b) noexcept {
    NormalEquations eq{};
    const Mat3 w = matrix_of(p);
    const Vec3 v0 = offset_of(p);

    for (const Vec3& raw : samples) {
        const Vec3 d = raw - v0;
        const Vec3 cal = w * d;
        const float cal_norm = std::max(cal.norm(), 1e-4F);   // точка сіла в центр
        const float r = cal_norm - earth_b;
        eq.cost += r * r;

        // u = ∂‖cal‖/∂cal — одиничний вектор уздовж скоригованого поля
        const Vec3 u = cal * (1.0F / cal_norm);

        const ParamVector jac{
            // ∂r/∂V0 = −Wᵀu, і W симетрична
            -(u.x * w.at(0, 0) + u.y * w.at(1, 0) + u.z * w.at(2, 0)),
            -(u.x * w.at(0, 1) + u.y * w.at(1, 1) + u.z * w.at(2, 1)),
            -(u.x * w.at(0, 2) + u.y * w.at(1, 2) + u.z * w.at(2, 2)),
            u.x * d.x,                  // W11
            u.x * d.y + u.y * d.x,      // W12 сидить одразу в (0,1) і (1,0)
            u.x * d.z + u.z * d.x,      // W13
            u.y * d.y,                  // W22
            u.y * d.z + u.z * d.y,      // W23
            u.z * d.z                   // W33
        };

        for (std::size_t j = 0; j < kParams; ++j) {
            eq.gradient[j] += jac[j] * r;
            for (std::size_t k = j; k < kParams; ++k) {   // симетрія: пів матриці
                eq.hessian[j][k] += jac[j] * jac[k];
            }
        }
    }

    for (std::size_t j = 1; j < kParams; ++j) {
        for (std::size_t k = 0; k < j; ++k) {
            eq.hessian[j][k] = eq.hessian[k][j];
        }
    }
    return eq;
}

[[nodiscard]] Calibration summarize(std::span<const Vec3> samples,
                                    const ParamVector& p, float earth_b,
                                    float coverage_pct, std::uint8_t iterations) noexcept {
    Calibration cal{};
    cal.offset = offset_of(p);
    cal.soft_iron = matrix_of(p);
    cal.earth_field = earth_b;
    cal.coverage_pct = coverage_pct;
    cal.points_used = static_cast<std::uint16_t>(samples.size());
    cal.iterations = iterations;

    float sum_sq = 0.0F;
    float sum_radius = 0.0F;
    for (const Vec3& raw : samples) {
        const float modulus = (cal.soft_iron * (raw - cal.offset)).norm();
        const float err = modulus - earth_b;
        sum_sq += err * err;
        sum_radius += modulus;
    }

    const float inv_n = 1.0F / static_cast<float>(samples.size());
    cal.rms_residual = std::sqrt(sum_sq * inv_n);
    cal.sphere_radius = sum_radius * inv_n;
    cal.condition = cal.soft_iron.condition_number();
    return cal;
}

}  // namespace

std::string_view describe(SolveError error) noexcept {
    switch (error) {
        case SolveError::LowCoverage:    return "мале покриття сфери";
        case SolveError::FewSamples:     return "замало точок";
        case SolveError::SingularSystem: return "вироджені нормальні рівняння";
        case SolveError::Diverged:       return "розбіжність параметрів";
        case SolveError::NoConvergence:  return "не збігся за ліміт ітерацій";
        case SolveError::PoorFitness:    return "завелика нев'язка RMS";
        case SolveError::IllConditioned: return "погана зумовленість W";
    }
    return "невідома помилка";
}

std::expected<Calibration, SolveFailure> fit_ellipsoid(std::span<const Vec3> samples,
                                                       float earth_field_ut,
                                                       float coverage_pct) noexcept {
    if (coverage_pct < limits::kMinCoveragePct) {
        return std::unexpected(SolveFailure{SolveError::LowCoverage, {}});
    }
    if (samples.size() < limits::kMinSamples) {
        return std::unexpected(SolveFailure{SolveError::FewSamples, {}});
    }

    // Початкове наближення: центр — вибіркове середнє хмари, W — одинична.
    // Просторове квотування робить це середнє чесною оцінкою центра сфери.
    Vec3 sum{};
    for (const Vec3& raw : samples) {
        sum = sum + raw;
    }
    const Vec3 mean = sum * (1.0F / static_cast<float>(samples.size()));

    ParamVector p{mean.x, mean.y, mean.z, 1.0F, 0.0F, 0.0F, 1.0F, 0.0F, 1.0F};

    float lambda = kLambdaStart;
    bool converged = false;
    bool singular = false;
    std::uint8_t accepted = 0;

    for (int iter = 0; iter < kMaxIterations && !converged && !singular; ++iter) {
        const NormalEquations eq = accumulate(samples, p, earth_field_ut);
        float cost = eq.cost;
        bool step_taken = false;

        for (int attempt = 0; attempt < kMaxDampingTries && !step_taken && !singular;
             ++attempt) {
            // Демпфування Марквардта масштабує саме діагональ, тож крок
            // лишається інваріантним до одиниць окремих параметрів.
            NormalMatrix damped = eq.hessian;
            ParamVector rhs{};
            for (std::size_t i = 0; i < kParams; ++i) {
                damped[i][i] += lambda * (eq.hessian[i][i] + 1e-3F);
                rhs[i] = -eq.gradient[i];
            }

            const auto step = solve_linear<kParams>(damped, rhs);
            if (!step) {
                // Головний елемент помер: піднімаємо λ вдесятеро, матриця
                // стає діагонально домінантною, метод — градієнтним спуском.
                lambda *= 10.0F;
                singular = lambda > kLambdaMax;
                continue;
            }

            ParamVector candidate{};
            float step_sq = 0.0F;
            for (std::size_t i = 0; i < kParams; ++i) {
                candidate[i] = p[i] + (*step)[i];
                step_sq += (*step)[i] * (*step)[i];
            }

            if (!plausible(candidate)) {
                lambda *= 10.0F;
                singular = lambda > kLambdaMax;
                continue;
            }

            const float trial_cost = cost_of(samples, candidate, earth_field_ut);
            if (trial_cost >= cost) {
                lambda *= 10.0F;   // крок завеликий — відкочуємо
                singular = lambda > kLambdaMax;
                continue;
            }

            const float gain = (cost - trial_cost) / (cost > 0.0F ? cost : 1.0F);
            p = candidate;
            cost = trial_cost;
            lambda = std::max(lambda * 0.2F, kLambdaMin);
            ++accepted;
            step_taken = true;
            converged = std::sqrt(step_sq) < 1e-4F || gain < 1e-6F;
        }

        if (!step_taken) {
            converged = true;   // жодне демпфування не допомогло, рухатись нікуди
        }
    }

    Calibration cal = summarize(samples, p, earth_field_ut, coverage_pct, accepted);

    if (singular) {
        return std::unexpected(SolveFailure{SolveError::SingularSystem, cal});
    }
    if (!std::isfinite(cal.rms_residual) || !plausible(p)) {
        return std::unexpected(SolveFailure{SolveError::Diverged, cal});
    }
    if (accepted == 0) {
        return std::unexpected(SolveFailure{SolveError::NoConvergence, cal});
    }
    if (cal.rms_residual > limits::kMaxRmsUt) {
        return std::unexpected(SolveFailure{SolveError::PoorFitness, cal});
    }
    if (cal.condition >= limits::kMaxCondition) {
        return std::unexpected(SolveFailure{SolveError::IllConditioned, cal});
    }

    cal.valid = true;
    return cal;
}

}  // namespace mag_cal
