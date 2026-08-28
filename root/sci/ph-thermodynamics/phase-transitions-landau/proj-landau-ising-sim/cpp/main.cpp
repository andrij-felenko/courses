#include <iostream>
#include <vector>
#include <cmath>
#include <random>
#include <iomanip>
#include <string>

// Клас розрахунку термодинамічного потенціалу Ландау
class LandauPotential {
public:
    double a0;
    double b;
    double Tc;

    LandauPotential(double a0_val, double b_val, double Tc_val)
        : a0(a0_val), b(b_val), Tc(Tc_val) {}

    // Термодинамічний потенціал Phi(eta)
    double energy(double T, double eta, double H = 0.0) const {
        double a = a0 * (T - Tc);
        return a * eta * eta + 0.5 * b * std::pow(eta, 4) - eta * H;
    }

    // Чисельна мінімізація методом Ньютона — Рафсона
    double find_equilibrium_eta(double T, double H = 0.0, double eta_init = 0.8) const {
        if (T >= Tc && std::abs(H) < 1e-9) {
            return 0.0;
        }

        double eta = (T < Tc && eta_init == 0.0) ? std::sqrt(a0 * (Tc - T) / b) : eta_init;
        double a = a0 * (T - Tc);

        for (int iter = 0; iter < 100; ++iter) {
            double grad = 2.0 * a * eta + 2.0 * b * std::pow(eta, 3) - H;
            double hessian = 2.0 * a + 6.0 * b * eta * eta;

            if (std::abs(hessian) < 1e-12) break;

            double step = grad / hessian;
            eta -= step;

            if (std::abs(step) < 1e-9) break;
        }
        return eta;
    }

    // Теплоємність Cp(T)
    double heat_capacity(double T, double C0 = 1.0) const {
        if (T >= Tc) {
            return C0;
        } else {
            return C0 + (a0 * a0 * T) / b;
        }
    }
};

// Симулятор 2D моделі Ізинґа методом Монте-Карло (Метрополіс)
class IsingModel2D {
private:
    int L;
    double J;
    std::vector<int> spins;
    std::mt19937 rng;
    std::uniform_real_distribution<double> dist_real;
    std::uniform_int_distribution<int> dist_int;

public:
    IsingModel2D(int lattice_size, double coupling = 1.0, unsigned int seed = 42)
        : L(lattice_size), J(coupling), spins(lattice_size * lattice_size, 1),
          rng(seed), dist_real(0.0, 1.0), dist_int(0, lattice_size * lattice_size - 1) {}

    int get_spin(int x, int y) const {
        int cx = (x + L) % L;
        int cy = (y + L) % L;
        return spins[cy * L + cx];
    }

    void sweep(double T, double H = 0.0) {
        int N = L * L;
        double beta = 1.0 / T;

        for (int k = 0; k < N; ++k) {
            int idx = dist_int(rng);
            int x = idx % L;
            int y = idx / L;

            int s = spins[idx];
            int sum_neighbors = get_spin(x + 1, y) + get_spin(x - 1, y) +
                                get_spin(x, y + 1) + get_spin(x, y - 1);

            double dE = 2.0 * s * (J * sum_neighbors + H);

            if (dE <= 0.0 || dist_real(rng) < std::exp(-dE * beta)) {
                spins[idx] = -s;
            }
        }
    }

    double calculate_magnetization() const {
        double sum = 0.0;
        for (int s : spins) sum += s;
        return std::abs(sum) / (L * L);
    }
};

int main() {
    std::cout << "=== 1. Мінімізація потенціалу Ландау ===" << std::endl;
    LandauPotential landau(1.0, 1.0, 2.269); // Tc для 2D Ізинґа ~ 2.269 J/kB

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "T / Tc\t\tT [K]\t\teta (Ландау)\tCp" << std::endl;
    std::cout << "------------------------------------------------" << std::endl;

    for (double rel_T = 0.5; rel_T <= 1.4; rel_T += 0.1) {
        double T = rel_T * landau.Tc;
        double eta = landau.find_equilibrium_eta(T);
        double Cp = landau.heat_capacity(T);
        std::cout << rel_T << "\t\t" << T << "\t\t" << eta << "\t\t" << Cp << std::endl;
    }

    std::cout << "\n=== 2. Монте-Карло симуляція 2D Ізинґа (L=32) ===" << std::endl;
    IsingModel2D ising(32, 1.0);
    double Tc_exact = 2.269;

    std::cout << "T / Tc\t\tT [J/kB]\t|M| (Monte-Carlo)" << std::endl;
    std::cout << "------------------------------------------------" << std::endl;

    for (double rel_T : {0.6, 0.8, 0.95, 1.0, 1.05, 1.2, 1.4}) {
        double T = rel_T * Tc_exact;

        // Термалізація (1000 кроків)
        for (int step = 0; step < 1000; ++step) {
            ising.sweep(T);
        }

        // Усереднення (1000 кроків)
        double avg_M = 0.0;
        for (int step = 0; step < 1000; ++step) {
            ising.sweep(T);
            avg_M += ising.calculate_magnetization();
        }
        avg_M /= 1000.0;

        std::cout << rel_T << "\t\t" << T << "\t\t" << avg_M << std::endl;
    }

    return 0;
}
