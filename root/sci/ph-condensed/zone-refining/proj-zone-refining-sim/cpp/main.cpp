#include <iostream>
#include <vector>
#include <numeric>
#include <iomanip>
#include <algorithm>
#include <cmath>

class ZoneRefiningSimulator {
public:
    struct Config {
        std::size_t num_cells{100};
        std::size_t zone_cells{10};
        double k_eff{0.10};
        double initial_conc{1.0};
    };

    explicit ZoneRefiningSimulator(Config config)
        : cfg_(config), concentration_(config.num_cells, config.initial_conc) {}

    void run_passes(std::size_t passes) {
        for (std::size_t p = 0; p < passes; ++p) {
            execute_single_pass();
        }
    }

    [[nodiscard]] const std::vector<double>& get_concentration() const noexcept {
        return concentration_;
    }

    void print_profile() const {
        std::cout << "=== Профіль розпреділення домішок після зонної очистки ===\n";
        std::cout << std::fixed << std::setprecision(8);
        for (std::size_t i = 0; i < concentration_.size(); i += 10) {
            double x_rel = static_cast<double>(i) / static_cast<double>(concentration_.size());
            double purity = (concentration_[i] > 0.0) ? (1.0 / concentration_[i]) : 0.0;
            std::cout << "x/L = " << std::setw(4) << x_rel 
                      << " | C/C0 = " << std::setw(12) << concentration_[i]
                      << " | Очищення: " << std::setw(8) << std::setprecision(1) << purity << "x\n";
        }
        std::cout << "x/L = 1.00 | C/C0 = " << std::setw(12) << concentration_.back() 
                  << " | Зона накопичення\n";
    }

private:
    Config cfg_;
    std::vector<double> concentration_;

    void execute_single_pass() {
        std::vector<double> c_next = concentration_;
        const auto M = cfg_.num_cells;
        const auto Nz = cfg_.zone_cells;
        const double k = cfg_.k_eff;

        /* 1. Фаза руху розплавленої зоної постійної довжини */
        for (std::size_t start = 0; start <= M - Nz; ++start) {
            double sum_mass = std::accumulate(c_next.begin() + start,
                                              c_next.begin() + start + Nz, 0.0);
            double c_L = sum_mass / static_cast<double>(Nz);
            double c_solid = k * c_L;
            concentration_[start] = c_solid;

            double rem_mass = sum_mass - c_solid;
            double c_rem_avg = rem_mass / static_cast<double>(Nz - 1);
            std::fill(c_next.begin() + start + 1, c_next.begin() + start + Nz, c_rem_avg);
        }

        /* 2. Фаза кристалізації залишкової зони (направлене затвердіння) */
        for (std::size_t start = M - Nz + 1; start < M - 1; ++start) {
            std::size_t Nz_curr = M - start;
            double sum_mass = std::accumulate(c_next.begin() + start, c_next.end(), 0.0);
            double c_L = sum_mass / static_cast<double>(Nz_curr);
            double c_solid = k * c_L;
            concentration_[start] = c_solid;

            double rem_mass = sum_mass - c_solid;
            double c_rem_avg = (Nz_curr > 1) ? (rem_mass / static_cast<double>(Nz_curr - 1)) : 0.0;
            std::fill(c_next.begin() + start + 1, c_next.end(), c_rem_avg);
        }

        /* Консервативне збереження маси для останнього вузла */
        double total_initial = std::accumulate(c_next.begin(), c_next.end(), 0.0);
        double crystallized = std::accumulate(concentration_.begin(), concentration_.end() - 1, 0.0);
        concentration_.back() = std::max(0.0, total_initial - crystallized);
    }
};

int main() {
    ZoneRefiningSimulator::Config cfg{
        .num_cells = 100, 
        .zone_cells = 10, 
        .k_eff = 0.10, 
        .initial_conc = 1.0
    };
    
    ZoneRefiningSimulator sim(cfg);
    sim.run_passes(10);
    sim.print_profile();

    return 0;
}
