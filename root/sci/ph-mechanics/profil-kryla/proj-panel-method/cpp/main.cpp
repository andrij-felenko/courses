#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <iomanip>
#include <algorithm>
#include <span>

struct Point {
    double x{0.0};
    double y{0.0};
};

struct Panel {
    Point p1;
    Point p2;
    Point cp;
    double length{0.0};
    double theta{0.0};
    Point normal;
    Point tangent;
    double gamma{0.0};
    double cp_val{0.0};
};

class PanelSolver {
public:
    PanelSolver(int m_digit, int p_digit, int t_digit, int num_panels)
        : m_{m_digit / 100.0}, p_{p_digit / 10.0}, t_{t_digit / 100.0}, num_panels_{num_panels} {
        generate_geometry();
    }

    void solve(double alpha_deg) {
        const double alpha = alpha_deg * std::numbers::pi / 180.0;
        const double v_inf_x = std::cos(alpha);
        const double v_inf_y = std::sin(alpha);

        std::vector<std::vector<double>> A(num_panels_, std::vector<double>(num_panels_, 0.0));
        std::vector<double> b(num_panels_, 0.0);

        for (int i = 0; i < num_panels_ - 1; ++i) {
            b[i] = -(v_inf_x * panels_[i].normal.x + v_inf_y * panels_[i].normal.y);
            for (int j = 0; j < num_panels_; ++j) {
                if (i != j) {
                    auto [u, v] = panel_velocity(panels_[j], panels_[i].cp.x, panels_[i].cp.y);
                    A[i][j] = u * panels_[i].normal.x + v * panels_[i].normal.y;
                }
            }
        }

        // Дискретна умова Кутти: сума циркуляцій на задній кромці дорівнює нулю
        A[num_panels_ - 1][0] = 1.0;
        A[num_panels_ - 1][num_panels_ - 1] = 1.0;
        b[num_panels_ - 1] = 0.0;

        std::vector<double> gamma(num_panels_, 0.0);
        solve_linear_system(A, b, gamma);

        cl_ = 0.0;
        cm_c4_ = 0.0;

        for (int i = 0; i < num_panels_; ++i) {
            panels_[i].gamma = gamma[i];
            double vt = v_inf_x * panels_[i].tangent.x + v_inf_y * panels_[i].tangent.y + 0.5 * gamma[i];
            for (int j = 0; j < num_panels_; ++j) {
                if (i != j) {
                    auto [u, v] = panel_velocity(panels_[j], panels_[i].cp.x, panels_[i].cp.y);
                    vt += (u * panels_[i].tangent.x + v * panels_[i].tangent.y) * gamma[j];
                }
            }
            panels_[i].cp_val = 1.0 - vt * vt;

            const double cp_ds = -panels_[i].cp_val * panels_[i].length;
            cl_ += cp_ds * panels_[i].normal.y;
            cm_c4_ += cp_ds * (panels_[i].normal.y * (panels_[i].cp.x - 0.25) - panels_[i].normal.x * panels_[i].cp.y);
        }
    }

    [[nodiscard]] double lift_coefficient() const noexcept { return cl_; }
    [[nodiscard]] double moment_coefficient() const noexcept { return cm_c4_; }
    [[nodiscard]] std::span<const Panel> panels() const noexcept { return panels_; }

private:
    double m_{0.0};
    double p_{0.0};
    double t_{0.0};
    int num_panels_{0};
    std::vector<Panel> panels_;
    double cl_{0.0};
    double cm_c4_{0.0};

    void generate_geometry() {
        const int half = num_panels_ / 2;
        std::vector<Point> nodes;
        nodes.reserve(num_panels_ + 1);

        auto compute_surface = [this](double x) {
            const double yt = 5.0 * t_ * (0.2969 * std::sqrt(x) - 0.1260 * x - 0.3516 * x * x + 0.2843 * x * x * x - 0.1015 * x * x * x * x);
            double yc = 0.0;
            double dy_dx = 0.0;
            if (p_ > 0.0 && m_ > 0.0) {
                if (x <= p_) {
                    yc = (m_ / (p_ * p_)) * (2.0 * p_ * x - x * x);
                    dy_dx = (2.0 * m_ / (p_ * p_)) * (p_ - x);
                } else {
                    yc = (m_ / ((1.0 - p_) * (1.0 - p_))) * ((1.0 - 2.0 * p_) + 2.0 * p_ * x - x * x);
                    dy_dx = (2.0 * m_ / ((1.0 - p_) * (1.0 - p_))) * (p_ - x);
                }
            }
            return std::make_tuple(yc, yt, std::atan(dy_dx));
        };

        // Нижня поверхня від TE до LE
        for (int i = 0; i <= half; ++i) {
            const double beta = (std::numbers::pi * i) / half;
            const double x = 0.5 * (1.0 + std::cos(beta));
            auto [yc, yt, th] = compute_surface(x);
            nodes.push_back({x + yt * std::sin(th), yc - yt * std::cos(th)});
        }

        // Верхня поверхня від LE до TE
        for (int i = 1; i <= half; ++i) {
            const double beta = (std::numbers::pi * i) / half;
            const double x = 0.5 * (1.0 - std::cos(beta));
            auto [yc, yt, th] = compute_surface(x);
            nodes.push_back({x - yt * std::sin(th), yc + yt * std::cos(th)});
        }

        panels_.resize(num_panels_);
        for (int i = 0; i < num_panels_; ++i) {
            panels_[i].p1 = nodes[i];
            panels_[i].p2 = nodes[i + 1];
            panels_[i].cp = {0.5 * (nodes[i].x + nodes[i + 1].x), 0.5 * (nodes[i].y + nodes[i + 1].y)};
            const double dx = nodes[i + 1].x - nodes[i].x;
            const double dy = nodes[i + 1].y - nodes[i].y;
            panels_[i].length = std::hypot(dx, dy);
            panels_[i].theta = std::atan2(dy, dx);
            panels_[i].tangent = {dx / panels_[i].length, dy / panels_[i].length};
            panels_[i].normal = {-panels_[i].tangent.y, panels_[i].tangent.x};
        }
    }

    static std::pair<double, double> panel_velocity(const Panel& p, double x, double y) noexcept {
        const double dx = x - p.p1.x;
        const double dy = y - p.p1.y;
        const double ct = std::cos(p.theta);
        const double st = std::sin(p.theta);

        const double x_loc = dx * ct + dy * st;
        const double y_loc = -dx * st + dy * ct;

        if (std::abs(y_loc) < 1e-10 && x_loc >= 0.0 && x_loc <= p.length) {
            return {0.0, 0.0};
        }

        const double r1_sq = x_loc * x_loc + y_loc * y_loc;
        const double r2_sq = (x_loc - p.length) * (x_loc - p.length) + y_loc * y_loc;

        const double theta1 = std::atan2(y_loc, x_loc);
        const double theta2 = std::atan2(y_loc, x_loc - p.length);

        const double u_loc = -(1.0 / (2.0 * std::numbers::pi)) * (theta2 - theta1);
        const double v_loc = (1.0 / (4.0 * std::numbers::pi)) * std::log(r2_sq / (r1_sq + 1e-15));

        return {u_loc * ct - v_loc * st, u_loc * st + v_loc * ct};
    }

    static bool solve_linear_system(std::vector<std::vector<double>>& A, std::vector<double>& b, std::vector<double>& x) {
        const int n = static_cast<int>(b.size());
        for (int i = 0; i < n; ++i) {
            int max_row = i;
            double max_val = std::abs(A[i][i]);
            for (int k = i + 1; k < n; ++k) {
                if (std::abs(A[k][i]) > max_val) {
                    max_val = std::abs(A[k][i]);
                    max_row = k;
                }
            }
            if (max_val < 1e-12) return false;

            std::swap(A[i], A[max_row]);
            std::swap(b[i], b[max_row]);

            for (int k = i + 1; k < n; ++k) {
                const double factor = A[k][i] / A[i][i];
                b[k] -= factor * b[i];
                for (int j = i; j < n; ++j) {
                    A[k][j] -= factor * A[i][j];
                }
            }
        }

        for (int i = n - 1; i >= 0; --i) {
            double sum = 0.0;
            for (int j = i + 1; j < n; ++j) {
                sum += A[i][j] * x[j];
            }
            x[i] = (b[i] - sum) / A[i][i];
        }
        return true;
    }
};

int main() {
    PanelSolver solver(2, 4, 12, 40); // NACA 2412, 40 панелей
    solver.solve(5.0);

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "NACA 2412 | Alpha: 5.0 deg | Panels: 40\n";
    std::cout << "Cl: " << solver.lift_coefficient() << " | Cm(c/4): " << solver.moment_coefficient() << "\n";
    std::cout << "-----------------------------------------\n";
    std::cout << "Panel   x/c        Cp (Нижня / Верхня)\n";

    const auto panels = solver.panels();
    for (size_t i = 0; i < panels.size(); i += 4) {
        std::cout << std::setw(3) << i << "    "
                  << std::setw(6) << std::setprecision(3) << panels[i].cp.x << "    "
                  << std::showpos << std::setw(7) << panels[i].cp_val << std::noshowpos << "\n";
    }
    return 0;
}
