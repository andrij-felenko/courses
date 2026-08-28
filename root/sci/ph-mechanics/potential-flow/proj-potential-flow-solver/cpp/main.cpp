#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <iomanip>
#include <memory>
#include <stdexcept>

struct Panel {
    double x1{}, y1{};
    double x2{}, y2{};
    double xc{}, yc{};
    double len{};
    double beta{};
    double nx{}, ny{};
    double tx{}, ty{};
    double q{};
    double vt{};
    double cp{};
};

class PanelSolver {
public:
    PanelSolver(int num_panels, double radius, double u_infinity)
        : n_(num_panels), radius_(radius), u_inf_(u_infinity) {
        if (n_ <= 0) throw std::invalid_argument("Кількість панелей має бути більшою за нуль");
        generate_geometry();
    }

    void solve() {
        std::vector<std::vector<double>> A(n_, std::vector<double>(n_, 0.0));
        std::vector<double> b(n_, 0.0);

        for (int i = 0; i < n_; ++i) {
            b[i] = -u_inf_ * panels_[i].nx;
            for (int j = 0; j < n_; ++j) {
                if (i == j) {
                    A[i][j] = 0.5;
                } else {
                    const double dx = panels_[i].xc - panels_[j].xc;
                    const double dy = panels_[i].yc - panels_[j].yc;
                    const double r2 = dx * dx + dy * dy;
                    const double vn = (dx * panels_[i].nx + dy * panels_[i].ny) / (2.0 * std::numbers::pi * r2);
                    A[i][j] = vn * panels_[j].len;
                }
            }
        }

        std::vector<double> q = gaussian_elimination(A, b);

        for (int i = 0; i < n_; ++i) {
            panels_[i].q = q[i];
            double vt = u_inf_ * panels_[i].tx;
            for (int j = 0; j < n_; ++j) {
                if (i != j) {
                    const double dx = panels_[i].xc - panels_[j].xc;
                    const double dy = panels_[i].yc - panels_[j].yc;
                    const double r2 = dx * dx + dy * dy;
                    const double vt_ind = (dx * panels_[i].tx + dy * panels_[i].ty) / (2.0 * std::numbers::pi * r2);
                    vt += q[j] * vt_ind * panels_[j].len;
                }
            }
            panels_[i].vt = vt;
            panels_[i].cp = 1.0 - (vt / u_inf_) * (vt / u_inf_);
        }
    }

    const std::vector<Panel>& panels() const noexcept { return panels_; }

private:
    void generate_geometry() {
        panels_.resize(n_);
        for (int i = 0; i < n_; ++i) {
            const double theta1 = 2.0 * std::numbers::pi * i / n_;
            const double theta2 = 2.0 * std::numbers::pi * (i + 1) / n_;

            panels_[i].x1 = radius_ * std::cos(theta1);
            panels_[i].y1 = radius_ * std::sin(theta1);
            panels_[i].x2 = radius_ * std::cos(theta2);
            panels_[i].y2 = radius_ * std::sin(theta2);

            panels_[i].xc = 0.5 * (panels_[i].x1 + panels_[i].x2);
            panels_[i].yc = 0.5 * (panels_[i].y1 + panels_[i].y2);

            const double dx = panels_[i].x2 - panels_[i].x1;
            const double dy = panels_[i].y2 - panels_[i].y1;
            panels_[i].len = std::hypot(dx, dy);
            panels_[i].beta = std::atan2(dy, dx);

            panels_[i].tx = dx / panels_[i].len;
            panels_[i].ty = dy / panels_[i].len;
            panels_[i].nx = -panels_[i].ty;
            panels_[i].ny =  panels_[i].tx;
        }
    }

    std::vector<double> gaussian_elimination(std::vector<std::vector<double>> A, std::vector<double> b) {
        const int n = static_cast<int>(b.size());
        for (int i = 0; i < n; ++i) {
            int max_row = i;
            for (int k = i + 1; k < n; ++k) {
                if (std::abs(A[k][i]) > std::abs(A[max_row][i])) {
                    max_row = k;
                }
            }
            std::swap(A[i], A[max_row]);
            std::swap(b[i], b[max_row]);

            for (int k = i + 1; k < n; ++k) {
                const double factor = -A[k][i] / A[i][i];
                for (int j = i; j < n; ++j) {
                    if (i == j) {
                        A[k][j] = 0.0;
                    } else {
                        A[k][j] += factor * A[i][j];
                    }
                }
                b[k] += factor * b[i];
            }
        }

        std::vector<double> x(n, 0.0);
        for (int i = n - 1; i >= 0; --i) {
            x[i] = b[i] / A[i][i];
            for (int k = i - 1; k >= 0; --k) {
                b[k] -= A[k][i] * x[i];
            }
        }
        return x;
    }

    int n_;
    double radius_;
    double u_inf_;
    std::vector<Panel> panels_;
};

int main() {
    try {
        constexpr int num_panels = 36;
        constexpr double radius = 1.0;
        constexpr double u_infinity = 10.0;

        PanelSolver solver(num_panels, radius, u_infinity);
        solver.solve();

        std::cout << "Результати розрахунку потенціального обтікання циліндра (C++):\n";
        std::cout << std::setw(8) << "Панель" << " | "
                  << std::setw(10) << "Xc" << " | "
                  << std::setw(10) << "Yc" << " | "
                  << std::setw(17) << "Cp (чисельний)" << " | "
                  << std::setw(17) << "Cp (аналітичний)" << "\n";
        std::cout << std::string(70, '-') << "\n";

        const auto& panels = solver.panels();
        for (std::size_t i = 0; i < panels.size(); i += 4) {
            const double theta = std::atan2(panels[i].yc, panels[i].xc);
            const double cp_exact = 1.0 - 4.0 * std::sin(theta) * std::sin(theta);
            std::cout << std::setw(8) << i << " | "
                      << std::setw(10) << std::fixed << std::setprecision(4) << panels[i].xc << " | "
                      << std::setw(10) << panels[i].yc << " | "
                      << std::setw(17) << panels[i].cp << " | "
                      << std::setw(17) << cp_exact << "\n";
        }
    } catch (const std::exception& e) {
        std::cerr << "Помилка: " << e.what() << "\n";
        return 1;
    }
    return 0;
}
