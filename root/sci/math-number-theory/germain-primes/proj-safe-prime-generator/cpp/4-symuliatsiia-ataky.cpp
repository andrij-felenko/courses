#include <iostream>
#include <cmath>
#include <iomanip>
#include <cstdint>

namespace crypto::analysis {

struct ModuleMetrics {
    std::uint64_t modulus;
    std::uint64_t max_factor;
    double operations_cost;
};

class PohligHellmanAnalyzer {
public:
    static ModuleMetrics evaluate_smooth(std::uint64_t q, std::uint64_t max_p_i) {
        return ModuleMetrics{q, max_p_i, std::sqrt(static_cast<double>(max_p_i))};
    }

    static ModuleMetrics evaluate_safe(std::uint64_t p) {
        std::uint64_t q = 2 * p + 1;
        return ModuleMetrics{q, p, std::sqrt(static_cast<double>(p))};
    }
};

} // namespace crypto::analysis

int main() {
    using namespace crypto::analysis;

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "=== Симуляція стійкості Поліга — Геллмана (C++20) ===\n\n";

    auto smooth_res = PohligHellmanAnalyzer::evaluate_smooth(180181, 13);
    auto safe_res = PohligHellmanAnalyzer::evaluate_safe(500000003);

    std::cout << "Гладкий модуль q = " << smooth_res.modulus 
              << " (max factor = " << smooth_res.max_factor << "):\n"
              << "  Складність атаки: " << smooth_res.operations_cost << " операцій.\n\n";

    std::cout << "Безпечний модуль q = " << safe_res.modulus 
              << " (p = " << safe_res.max_factor << "):\n"
              << "  Складність атаки: " << safe_res.operations_cost << " операцій.\n\n";

    double ratio = safe_res.operations_cost / smooth_res.operations_cost;
    std::cout << "Висновок: Використання безпечного модуля збільшує стійкість у " 
              << ratio << " разів!\n";

    return 0;
}
