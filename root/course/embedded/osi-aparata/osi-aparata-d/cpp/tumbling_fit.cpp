#include "tumbling_fit.hpp"

#include <algorithm>
#include <cmath>
#include <iterator>
#include <numeric>
#include <utility>

namespace {

// Параметри: p[0..5] — m00, m10, m11, m20, m21, m22; p[6..8] — зсув.
// Рахуємо в double: калібрування йде раз на стенді, а елементи нормальних
// рівнянь мають порядок g⁴ і у float погано обумовлені.
using Params = std::array<double, 9>;
using Jacobian = std::array<double, 9>;

constexpr std::array<int, 6> kActiveDiagonal{0, 2, 5, 6, 7, 8};
constexpr std::array<int, 9> kActiveFull{0, 1, 2, 3, 4, 5, 6, 7, 8};

double residual(const Params& p, const nav::Vector3& a, double g2, Jacobian* jac) noexcept {
    const double ux = static_cast<double>(a.x) - p[6];
    const double uy = static_cast<double>(a.y) - p[7];
    const double uz = static_cast<double>(a.z) - p[8];
    const double y0 = p[0] * ux;
    const double y1 = p[1] * ux + p[2] * uy;
    const double y2 = p[3] * ux + p[4] * uy + p[5] * uz;
    if (jac != nullptr) {
        (*jac)[0] = 2.0 * y0 * ux;
        (*jac)[1] = 2.0 * y1 * ux;
        (*jac)[2] = 2.0 * y1 * uy;
        (*jac)[3] = 2.0 * y2 * ux;
        (*jac)[4] = 2.0 * y2 * uy;
        (*jac)[5] = 2.0 * y2 * uz;
        (*jac)[6] = -2.0 * (p[0] * y0 + p[1] * y1 + p[3] * y2);
        (*jac)[7] = -2.0 * (p[2] * y1 + p[4] * y2);
        (*jac)[8] = -2.0 * (p[5] * y2);
    }
    return y0 * y0 + y1 * y1 + y2 * y2 - g2;
}

double total_cost(const Params& p, std::span<const nav::Vector3> a, double g2) noexcept {
    double sum = 0.0;
    for (const auto& sample : a) {
        const double r = residual(p, sample, g2, nullptr);
        sum += r * r;
    }
    return sum;
}

// Гаус із частковим вибором головного елемента над активними параметрами.
std::optional<Params> solve_dense(std::array<Params, 9> h, Params rhs, int na) noexcept {
    std::array<std::array<double, 10>, 9> aug{};
    for (int i = 0; i < na; ++i) {
        for (int j = 0; j < na; ++j) aug[i][j] = h[i][j];
        aug[i][na] = rhs[i];
    }
    for (int c = 0; c < na; ++c) {
        int pivot = c;
        for (int r = c + 1; r < na; ++r) {
            if (std::fabs(aug[r][c]) > std::fabs(aug[pivot][c])) pivot = r;
        }
        if (std::fabs(aug[pivot][c]) < 1e-14) return std::nullopt;
        std::swap(aug[c], aug[pivot]);
        for (int r = c + 1; r < na; ++r) {
            const double k = aug[r][c] / aug[c][c];
            if (k == 0.0) continue;
            for (int j = c; j <= na; ++j) aug[r][j] -= k * aug[c][j];
        }
    }
    Params out{};
    for (int i = na - 1; i >= 0; --i) {
        double s = aug[i][na];
        for (int j = i + 1; j < na; ++j) s -= aug[i][j] * out[j];
        out[i] = s / aug[i][i];
        if (!std::isfinite(out[i])) return std::nullopt;
    }
    return out;
}

struct Box {
    std::array<float, 3> lo{};
    std::array<float, 3> hi{};
};

Box bounding_box(std::span<const nav::Vector3> a) noexcept {
    Box box{{a[0].x, a[0].y, a[0].z}, {a[0].x, a[0].y, a[0].z}};
    for (const auto& v : a) {
        const std::array<float, 3> c{v.x, v.y, v.z};
        for (int k = 0; k < 3; ++k) {
            box.lo[k] = std::min(box.lo[k], c[k]);
            box.hi[k] = std::max(box.hi[k], c[k]);
        }
    }
    return box;
}

// Усі шість граней мають бути в наборі: інакше еліпсоїд не закріплений по всіх осях.
bool faces_covered(std::span<const nav::Vector3> a, const Box& box, float g) noexcept {
    std::array<bool, 6> face{};
    for (const auto& v : a) {
        const std::array<float, 3> c{v.x, v.y, v.z};
        std::array<float, 3> d{};
        int dominant = 0;
        float best = 0.0F;
        for (int k = 0; k < 3; ++k) {
            d[k] = c[k] - 0.5F * (box.lo[k] + box.hi[k]);
            if (std::fabs(d[k]) > best) {
                best = std::fabs(d[k]);
                dominant = k;
            }
        }
        if (best < 0.5F * g) continue;   // позиція не притиснута до жодної грані
        face[static_cast<std::size_t>(2 * dominant + (d[dominant] > 0.0F ? 0 : 1))] = true;
    }
    return std::ranges::all_of(face, [](bool f) { return f; });
}

}  // namespace

namespace nav {

std::string_view describe(FitError e) noexcept {
    switch (e) {
        case FitError::TooFewPositions:         return "замало положень для обраної моделі";
        case FitError::FacesNotCovered:         return "положення не покривають усі шість граней";
        case FitError::BadSample:               return "серед вимірів є нескінченні значення";
        case FitError::SingularNormalEquations: return "вироджені нормальні рівняння";
        case FitError::NoConvergence:           return "ітерації не зійшлися";
    }
    return "невідомий стан";
}

std::expected<TumbleFit, FitError> fit_static_positions(std::span<const Vector3> averages,
                                                        float gravity, SensorModel model) {
    const int need = (model == SensorModel::Triaxial) ? 9 : 6;
    if (std::ssize(averages) < need) return std::unexpected(FitError::TooFewPositions);
    if (!(gravity > 0.0F) || !std::isfinite(gravity)) return std::unexpected(FitError::BadSample);
    if (!std::ranges::all_of(averages, [](const Vector3& v) { return v.finite(); })) {
        return std::unexpected(FitError::BadSample);
    }

    const Box box = bounding_box(averages);
    if (!faces_covered(averages, box, gravity)) return std::unexpected(FitError::FacesNotCovered);

    const int na = (model == SensorModel::Triaxial) ? 9 : 6;
    const auto active = [&](int i) {
        return (model == SensorModel::Triaxial) ? kActiveFull[static_cast<std::size_t>(i)]
                                                : kActiveDiagonal[static_cast<std::size_t>(i)];
    };

    // Початкове наближення: центр коробки — зсув, півширина — обернений масштаб.
    Params p{1.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0};
    constexpr std::array<int, 3> kDiag{0, 2, 5};
    for (int k = 0; k < 3; ++k) {
        const double half = 0.5 * (static_cast<double>(box.hi[k]) - static_cast<double>(box.lo[k]));
        if (half < 1e-6) return std::unexpected(FitError::FacesNotCovered);
        p[static_cast<std::size_t>(kDiag[k])] = static_cast<double>(gravity) / half;
        p[static_cast<std::size_t>(6 + k)] =
            0.5 * (static_cast<double>(box.hi[k]) + static_cast<double>(box.lo[k]));
    }

    const double g2 = static_cast<double>(gravity) * static_cast<double>(gravity);
    double lambda = 1e-3;
    double cost = total_cost(p, averages, g2);
    bool converged = false;
    int iteration = 0;

    for (; iteration < 100 && !converged; ++iteration) {
        std::array<Params, 9> h{};
        Params grad{};
        for (const auto& sample : averages) {
            Jacobian jac{};
            const double r = residual(p, sample, g2, &jac);
            for (int i = 0; i < na; ++i) {
                const double ji = jac[static_cast<std::size_t>(active(i))];
                grad[static_cast<std::size_t>(i)] += ji * r;
                for (int j = 0; j < na; ++j) {
                    h[static_cast<std::size_t>(i)][static_cast<std::size_t>(j)] +=
                        ji * jac[static_cast<std::size_t>(active(j))];
                }
            }
        }
        std::array<Params, 9> damped = h;
        Params rhs{};
        for (int i = 0; i < na; ++i) {
            damped[static_cast<std::size_t>(i)][static_cast<std::size_t>(i)] *= (1.0 + lambda);
            rhs[static_cast<std::size_t>(i)] = -grad[static_cast<std::size_t>(i)];
        }

        const auto delta = solve_dense(damped, rhs, na);
        if (!delta) return std::unexpected(FitError::SingularNormalEquations);

        Params trial = p;
        for (int i = 0; i < na; ++i) {
            trial[static_cast<std::size_t>(active(i))] += (*delta)[static_cast<std::size_t>(i)];
        }
        const double trial_cost = total_cost(trial, averages, g2);

        if (std::isfinite(trial_cost) && trial_cost < cost) {
            const double gain = cost - trial_cost;
            p = trial;
            cost = trial_cost;
            lambda = std::max(lambda / 3.0, 1e-9);
            if (gain < 1e-12 * (1.0 + cost)) converged = true;
        } else {
            lambda *= 5.0;
            if (lambda > 1e9) break;   // крок нікуди не веде, далі лише марні ітерації
        }
    }
    if (!converged) return std::unexpected(FitError::NoConvergence);

    // Діагональ M мусить бути додатною: зміна знака осі — дзеркало, а не масштаб.
    for (const int k : kDiag) {
        if (p[static_cast<std::size_t>(k)] <= 0.0) {
            return std::unexpected(FitError::SingularNormalEquations);
        }
    }

    TumbleFit fit{};
    fit.m = Matrix3{{{{static_cast<float>(p[0]), 0.0F, 0.0F},
                      {static_cast<float>(p[1]), static_cast<float>(p[2]), 0.0F},
                      {static_cast<float>(p[3]), static_cast<float>(p[4]), static_cast<float>(p[5])}}}};
    fit.bias = Vector3{static_cast<float>(p[6]), static_cast<float>(p[7]), static_cast<float>(p[8])};
    fit.iterations = iteration;

    double acc = 0.0;
    for (const auto& sample : averages) {
        const double e = static_cast<double>((fit.m * (sample - fit.bias)).norm()) -
                         static_cast<double>(gravity);
        acc += e * e;
    }
    fit.rms_rel = static_cast<float>(std::sqrt(acc / static_cast<double>(averages.size())) /
                                     static_cast<double>(gravity));
    return fit;
}

std::optional<Vector3> still_average(std::span<const Vector3> samples, float tolerance) noexcept {
    if (samples.size() < 2 || !(tolerance > 0.0F)) return std::nullopt;
    if (!std::ranges::all_of(samples, [](const Vector3& v) { return v.finite(); })) {
        return std::nullopt;
    }
    const Vector3 sum = std::accumulate(samples.begin(), samples.end(), Vector3{},
                                        [](const Vector3& acc, const Vector3& v) { return acc + v; });
    const Vector3 mean = sum * (1.0F / static_cast<float>(samples.size()));
    const bool still = std::ranges::all_of(samples, [&](const Vector3& v) {
        return (v - mean).norm() <= tolerance;
    });
    // Апарат ворухнувся — позицію переписують, а не приймають «зате швидко».
    return still ? std::optional{mean} : std::nullopt;
}

}  // namespace nav
