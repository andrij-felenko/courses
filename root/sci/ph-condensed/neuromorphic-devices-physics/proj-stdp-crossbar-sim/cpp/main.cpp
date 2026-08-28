#include <iostream>
#include <vector>
#include <cmath>
#include <random>
#include <algorithm>
#include <iomanip>

class SynapticCrossbar {
public:
    struct Config {
        double g_min{1e-6};    // 1 мкСм (HRS)
        double g_max{100e-6};  // 100 мкСм (LRS)
        double a_plus{5e-6};   // Амплітуда LTP
        double a_minus{4e-6};  // Амплітуда LTD
        double tau_plus{20.0}; // мс
        double tau_minus{20.0};// мс
    };

    SynapticCrossbar(std::size_t rows, std::size_t cols, Config cfg = {})
        : rows_(rows), cols_(cols), cfg_(cfg), weights_(rows * cols) {
        
        std::mt19937 gen(42);
        std::uniform_real_distribution<double> dist(cfg_.g_min, cfg_.g_max);
        for (auto& g : weights_) {
            g = dist(gen);
        }
    }

    // Аналогове множення MVM: I_j = sum_i (V_i * G_ij)
    [[nodiscard]] std::vector<double> compute_mvm(const std::vector<double>& v_in) const {
        std::vector<double> i_out(cols_, 0.0);
        for (std::size_t j = 0; j < cols_; ++j) {
            for (std::size_t i = 0; i < rows_; ++i) {
                i_out[j] += v_in[i] * weights_[i * cols_ + j];
            }
        }
        return i_out;
    }

    // Оновлення провідностей за правилом STDP
    void update_stdp(const std::vector<double>& t_pre, const std::vector<double>& t_post) {
        for (std::size_t i = 0; i < rows_; ++i) {
            for (std::size_t j = 0; j < cols_; ++j) {
                const double dt = t_post[j] - t_pre[i];
                double dg = 0.0;

                if (dt > 0.0) {
                    dg = cfg_.a_plus * std::exp(-dt / cfg_.tau_plus);
                } else if (dt < 0.0) {
                    dg = -cfg_.a_minus * std::exp(dt / cfg_.tau_minus);
                }

                auto& g = weights_[i * cols_ + j];
                g = std::clamp(g + dg, cfg_.g_min, cfg_.g_max);
            }
        }
    }

private:
    std::size_t rows_;
    std::size_t cols_;
    Config cfg_;
    std::vector<double> weights_;
};

int main() {
    SynapticCrossbar crossbar(4, 4);

    const std::vector<double> v_in = {1.0, 0.5, 0.0, 1.2};
    
    std::cout << std::fixed << std::setprecision(4);
    std::cout << "=== До навчання: MVM аналогові струми ===\n";
    auto i_initial = crossbar.compute_mvm(v_in);
    for (std::size_t j = 0; j < i_initial.size(); ++j) {
        std::cout << "Стовпець " << j << ": Струм I = " << i_initial[j] * 1e6 << " мкА\n";
    }

    const std::vector<double> t_pre  = {10.0, 15.0, 30.0, 40.0};
    const std::vector<double> t_post = {25.0, 10.0, 35.0, 20.0};

    crossbar.update_stdp(t_pre, t_post);

    std::cout << "\n=== Після навчання STDP: Нові MVM аналогові струми ===\n";
    auto i_trained = crossbar.compute_mvm(v_in);
    for (std::size_t j = 0; j < i_trained.size(); ++j) {
        std::cout << "Стовпець " << j << ": Струм I = " << i_trained[j] * 1e6 << " мкА\n";
    }

    return 0;
}
