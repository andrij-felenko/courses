#include <iostream>
#include <vector>
#include <cmath>
#include <algorithm>

class ElectrostaticSolver2D {
private:
    int nx, ny;
    double h;
    double eps0 = 8.854187817e-12;
    double eps;
    
    std::vector<std::vector<double>> v;
    std::vector<std::vector<double>> rho;
    std::vector<std::vector<bool>> is_fixed;

public:
    ElectrostaticSolver2D(int nx_, int ny_, double h_, double eps_r = 1.0)
        : nx(nx_), ny(ny_), h(h_), eps(eps0 * eps_r),
          v(nx_, std::vector<double>(ny_, 0.0)),
          rho(nx_, std::vector<double>(ny_, 0.0)),
          is_fixed(nx_, std::vector<bool>(ny_, false)) {}

    void set_boundary_electrode(int x_min, int x_max, int y, double voltage) {
        for (int i = x_min; i <= x_max; ++i) {
            v[i][y] = voltage;
            is_fixed[i][y] = true;
        }
    }

    int solve_poisson(int max_iter = 5000, double tol = 1e-6, double omega = 1.85) {
        double h2 = h * h;
        for (int iter = 0; iter < max_iter; ++iter) {
            double max_diff = 0.0;
            for (int i = 1; i < nx - 1; ++i) {
                for (int j = 1; j < ny - 1; ++j) {
                    if (is_fixed[i][j]) continue;

                    double v_new = 0.25 * (v[i+1][j] + v[i-1][j] + 
                                           v[i][j+1] + v[i][j-1] + 
                                           (h2 * rho[i][j] / eps));
                    
                    double v_sor = v[i][j] + omega * (v_new - v[i][j]);
                    double diff = std::abs(v_sor - v[i][j]);
                    if (diff > max_diff) max_diff = diff;
                    v[i][j] = v_sor;
                }
            }
            if (max_diff < tol) return iter + 1;
        }
        return max_iter;
    }

    double compute_field_energy(double depthz = 1.0) const {
        double total_energy = 0.0;
        double inv_2h = 1.0 / (2.0 * h);
        double cell_vol = h * h * depthz;

        for (int i = 1; i < nx - 1; ++i) {
            for (int j = 1; j < ny - 1; ++j) {
                double ex = -(v[i+1][j] - v[i-1][j]) * inv_2h;
                double ey = -(v[i][j+1] - v[i][j-1]) * inv_2h;

                double e_sq = ex * ex + ey * ey;
                double w_e = 0.5 * eps * e_sq;
                total_energy += w_e * cell_vol;
            }
        }
        return total_energy;
    }
};

int main() {
    int nx = 100, ny = 100;
    double h = 0.001; // 1 мм
    ElectrostaticSolver2D solver(nx, ny, h, 2.2);

    solver.set_boundary_electrode(20, 80, 40, 100.0);
    solver.set_boundary_electrode(20, 80, 60, 0.0);

    int iters = solver.solve_poisson();
    double w_field = solver.compute_field_energy(0.1);

    std::cout << "Збіжність за " << iters << " ітерацій.\n";
    std::cout << "Обчислена енергія поля: " << w_field * 1e6 << " мкДж\n";
    return 0;
}
