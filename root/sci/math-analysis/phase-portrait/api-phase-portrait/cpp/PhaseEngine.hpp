// PhaseEngine.hpp — Високорівневий C++20 інтерфейс бібліотеки phase
#ifndef PHASE_ENGINE_HPP
#define PHASE_ENGINE_HPP

#include <array>
#include <vector>
#include <functional>
#include <expected>
#include <string_view>
#include <complex>

namespace phase {

enum class ErrorCode {
    NullPointer,
    InvalidParameter,
    Divergence,
    ConvergenceFailed,
    AllocationFailed
};

struct Point {
    double q{0.0};
    double p{0.0};

    [[nodiscard]] constexpr Point operator+(const Point& rhs) const noexcept {
        return {q + rhs.q, p + rhs.p};
    }
    [[nodiscard]] constexpr Point operator*(double s) const noexcept {
        return {q * s, p * s};
    }
};

struct Derivs {
    double dq_dt{0.0};
    double dp_dt{0.0};
};

using VectorField = std::function<Derivs(double t, const Point& state)>;

enum class SingularType {
    Saddle,
    Center,
    FocusStable,
    FocusUnstable,
    NodeStable,
    NodeUnstable,
    Degenerate
};

struct SingularAnalysis {
    Point location;
    std::array<std::array<double, 2>, 2> jacobian;
    double trace;
    double det;
    double discriminant;
    std::complex<double> lambda1;
    std::complex<double> lambda2;
    SingularType type;
};

struct GridConfig {
    double q_min{-5.0};
    double q_max{5.0};
    std::size_t q_steps{30};
    double p_min{-5.0};
    double p_max{5.0};
    std::size_t p_steps{30};
};

struct GridVector {
    Point point;
    Derivs derivs;
    double magnitude;
};

class SystemEngine {
public:
    explicit SystemEngine(VectorField field) : field_(std::move(field)) {}

    // Обчислення наступного стану за допомогою RK4
    [[nodiscard]] Point rk4_step(const Point& current, double t, double h) const noexcept {
        const auto k1 = field_(t, current);
        const Point p1{current.q + 0.5 * h * k1.dq_dt, current.p + 0.5 * h * k1.dp_dt};

        const auto k2 = field_(t + 0.5 * h, p1);
        const Point p2{current.q + 0.5 * h * k2.dq_dt, current.p + 0.5 * h * k2.dp_dt};

        const auto k3 = field_(t + 0.5 * h, p2);
        const Point p3{current.q + h * k3.dq_dt, current.p + h * k3.dp_dt};

        const auto k4 = field_(t + h, p3);

        return {
            current.q + (h / 6.0) * (k1.dq_dt + 2.0 * k2.dq_dt + 2.0 * k3.dq_dt + k4.dq_dt),
            current.p + (h / 6.0) * (k1.dp_dt + 2.0 * k2.dp_dt + 2.0 * k3.dp_dt + k4.dp_dt)
        };
    }

    // Інтегрування траєкторії із поверненням std::expected
    [[nodiscard]] std::expected<std::vector<Point>, ErrorCode>
    integrate(const Point& initial, double h, std::size_t steps) const {
        if (h <= 0.0 || steps == 0) {
            return std::unexpected(ErrorCode::InvalidParameter);
        }

        std::vector<Point> traj;
        traj.reserve(steps + 1);
        Point curr = initial;
        double t = 0.0;
        traj.push_back(curr);

        for (std::size_t i = 0; i < steps; ++i) {
            curr = rk4_step(curr, t, h);
            if (std::isnan(curr.q) || std::isnan(curr.p) || std::isinf(curr.q) || std::isinf(curr.p)) {
                return std::unexpected(ErrorCode::Divergence);
            }
            traj.push_back(curr);
            t += h;
        }

        return traj;
    }

    // Обчислення Якобіана та аналіз стійкості
    [[nodiscard]] std::expected<SingularAnalysis, ErrorCode>
    analyze_singular_point(const Point& eq_pt, double eps = 1e-6) const {
        const auto d0 = field_(0.0, eq_pt);
        if (std::hypot(d0.dq_dt, d0.dp_dt) > 1e-3) {
            return std::unexpected(ErrorCode::InvalidParameter); // Точка не є рівноважною
        }

        // Чисельне диференціювання для Якобіана
        const auto dq_plus  = field_(0.0, Point{eq_pt.q + eps, eq_pt.p});
        const auto dq_minus = field_(0.0, Point{eq_pt.q - eps, eq_pt.p});
        const auto dp_plus  = field_(0.0, Point{eq_pt.q, eq_pt.p + eps});
        const auto dp_minus = field_(0.0, Point{eq_pt.q, eq_pt.p - eps});

        double J00 = (dq_plus.dq_dt - dq_minus.dq_dt) / (2.0 * eps);
        double J01 = (dp_plus.dq_dt - dp_minus.dq_dt) / (2.0 * eps);
        double J10 = (dq_plus.dp_dt - dq_minus.dp_dt) / (2.0 * eps);
        double J11 = (dp_plus.dp_dt - dp_minus.dp_dt) / (2.0 * eps);

        double tr = J00 + J11;
        double det = J00 * J11 - J01 * J10;
        double discr = tr * tr - 4.0 * det;

        SingularAnalysis res{};
        res.location = eq_pt;
        res.jacobian = {{{J00, J01}, {J10, J11}}};
        res.trace = tr;
        res.det = det;
        res.discriminant = discr;

        if (discr >= 0.0) {
            res.lambda1 = std::complex<double>((tr + std::sqrt(discr)) / 2.0, 0.0);
            res.lambda2 = std::complex<double>((tr - std::sqrt(discr)) / 2.0, 0.0);
        } else {
            res.lambda1 = std::complex<double>(tr / 2.0,  std::sqrt(-discr) / 2.0);
            res.lambda2 = std::complex<double>(tr / 2.0, -std::sqrt(-discr) / 2.0);
        }

        // Класифікація
        if (det < 0.0) {
            res.type = SingularType::Saddle;
        } else if (std::abs(tr) < 1e-7 && discr < 0.0) {
            res.type = SingularType::Center;
        } else if (discr < 0.0) {
            res.type = (tr < 0.0) ? SingularType::FocusStable : SingularType::FocusUnstable;
        } else if (det > 0.0) {
            res.type = (tr < 0.0) ? SingularType::NodeStable : SingularType::NodeUnstable;
        } else {
            res.type = SingularType::Degenerate;
        }

        return res;
    }

private:
    VectorField field_;
};

} // namespace phase

#endif // PHASE_ENGINE_HPP
