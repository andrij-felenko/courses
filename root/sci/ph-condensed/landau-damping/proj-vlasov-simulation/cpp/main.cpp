#include <iostream>
#include <vector>
#include <cmath>
#include <numeric>
#include <iomanip>
#include <algorithm>

// Константи чисельної моделі плазми
constexpr double PI = 3.14159265358979323846;

struct PlasmaSimulationParams {
    std::size_t Nx = 64;         // Кількість вузлів по простору x
    std::size_t Nv = 128;        // Кількість вузлів по швидкості v
    double L = 2.0 * PI / 0.5;   // Довжина системи (для хвильового числа k = 0.5)
    double vmax = 6.0;           // Максимальна швидкість [-vmax, vmax]
    double dt = 0.1;             // Крок по часу
    double alpha = 0.05;         // Початкова амплітуда збурення
    double k = 0.5;              // Хвильове число збурення
};

class VlasovPoissonSolver {
private:
    PlasmaSimulationParams params_;
    double dx_, dv_;
    std::vector<double> x_grid_;
    std::vector<double> v_grid_;
    std::vector<double> f_;      // Двовимірний масив f[Nx * Nv]
    std::vector<double> E_;      // Електричне поле E[Nx]

    [[nodiscard]] std::size_t idx(std::size_t ix, std::size_t iv) const noexcept {
        return ix * params_.Nv + iv;
    }

    // Ініціалізація максвеллівського розподілу з синусоїдальним збуренням
    void initializeDistribution() {
        for (std::size_t ix = 0; ix < params_.Nx; ++ix) {
            double x = x_grid_[ix];
            double spatial_mod = 1.0 + params_.alpha * std::cos(params_.k * x);
            for (std::size_t iv = 0; iv < params_.Nv; ++iv) {
                double v = v_grid_[iv];
                double f0 = (1.0 / std::sqrt(2.0 * PI)) * std::exp(-0.5 * v * v);
                f_[idx(ix, iv)] = f0 * spatial_mod;
            }
        }
    }

    // 1D Сольвер Пуассона через сумму зарядів
    void solvePoisson() {
        std::vector<double> rho(params_.Nx, 0.0);
        for (std::size_t ix = 0; ix < params_.Nx; ++ix) {
            double n_e = 0.0;
            for (std::size_t iv = 0; iv < params_.Nv; ++iv) {
                n_e += f_[idx(ix, iv)] * dv_;
            }
            rho[ix] = 1.0 - n_e; // Іонний фон n_0 = 1.0
        }

        // Інтегрування dE/dx = rho для періодичних межевих умов
        E_[0] = 0.0;
        for (std::size_t ix = 0; ix < params_.Nx - 1; ++ix) {
            E_[ix + 1] = E_[ix] + rho[ix] * dx_;
        }
        
        // Видалення постійної складової (нульової гармоніки)
        double E_mean = std::accumulate(E_.begin(), E_.end(), 0.0) / params_.Nx;
        for (double& val : E_) {
            val -= E_mean;
        }
    }

    // Зсув уздовж просторової осі x (advection in x)
    void shiftX(double shift_dt) {
        std::vector<double> f_new(f_.size());
        for (std::size_t iv = 0; iv < params_.Nv; ++iv) {
            double v = v_grid_[iv];
            double shift_nodes = (v * shift_dt) / dx_;
            int int_shift = static_cast<int>(std::floor(shift_nodes));
            double frac = shift_nodes - int_shift;

            for (std::size_t ix = 0; ix < params_.Nx; ++ix) {
                int src_idx1 = (static_cast<int>(ix) - int_shift) % static_cast<int>(params_.Nx);
                if (src_idx1 < 0) src_idx1 += params_.Nx;
                int src_idx2 = (src_idx1 - 1 + params_.Nx) % params_.Nx;

                // Лінійна інтерполяція між вузлами
                f_new[idx(ix, iv)] = (1.0 - frac) * f_[idx(src_idx1, iv)] + frac * f_[idx(src_idx2, iv)];
            }
        }
        f_ = std::move(f_new);
    }

    // Зсув уздовж осі швидкостей v під дією поля E (advection in v)
    void shiftV(double shift_dt) {
        std::vector<double> f_new(f_.size());
        for (std::size_t ix = 0; ix < params_.Nx; ++ix) {
            double accel = -E_[ix]; // Для електронів a = -e E / m
            double shift_nodes = (accel * shift_dt) / dv_;
            int int_shift = static_cast<int>(std::floor(shift_nodes));
            double frac = shift_nodes - int_shift;

            for (std::size_t iv = 0; iv < params_.Nv; ++iv) {
                int src_idx1 = static_cast<int>(iv) - int_shift;
                int src_idx2 = src_idx1 - 1;

                double val1 = (src_idx1 >= 0 && src_idx1 < static_cast<int>(params_.Nv)) ? f_[idx(ix, src_idx1)] : 0.0;
                double val2 = (src_idx2 >= 0 && src_idx2 < static_cast<int>(params_.Nv)) ? f_[idx(ix, src_idx2)] : 0.0;

                f_new[idx(ix, iv)] = (1.0 - frac) * val1 + frac * val2;
            }
        }
        f_ = std::move(f_new);
    }

public:
    explicit VlasovPoissonSolver(PlasmaSimulationParams p)
        : params_(p),
          dx_(p.L / p.Nx),
          dv_((2.0 * p.vmax) / p.Nv),
          x_grid_(p.Nx),
          v_grid_(p.Nv),
          f_(p.Nx * p.Nv, 0.0),
          E_(p.Nx, 0.0) 
    {
        for (std::size_t i = 0; i < params_.Nx; ++i) {
            x_grid_[i] = i * dx_;
        }
        for (std::size_t j = 0; j < params_.Nv; ++j) {
            v_grid_[j] = -params_.vmax + (j + 0.5) * dv_;
        }
        initializeDistribution();
    }

    // Крок за методом расщеплення Ченга — Кнорра
    void step() {
        shiftX(0.5 * params_.dt);
        solvePoisson();
        shiftV(params_.dt);
        shiftX(0.5 * params_.dt);
    }

    // Розрахунок повної електростатичної енергії хвилі W_E = 0.5 * integral(E^2 dx)
    [[nodiscard]] double calculateFieldEnergy() const {
        double energy = 0.0;
        for (double val : E_) {
            energy += val * val * dx_;
        }
        return 0.5 * energy;
    }
};

int main() {
    PlasmaSimulationParams params;
    params.Nx = 64;
    params.Nv = 128;
    params.k = 0.5;
    params.dt = 0.1;

    VlasovPoissonSolver solver(params);

    std::cout << std::fixed << std::setprecision(6);
    std::cout << "# Час (t)\tЕнергія поля (W_E)\tln(W_E)\n";

    for (int step = 0; step <= 200; ++step) {
        double time = step * params.dt;
        double field_energy = solver.calculateFieldEnergy();
        
        if (step % 10 == 0) {
            double log_energy = (field_energy > 1e-15) ? std::log(field_energy) : -35.0;
            std::cout << time << "\t" << field_energy << "\t" << log_energy << "\n";
        }
        solver.step();
    }

    return 0;
}
