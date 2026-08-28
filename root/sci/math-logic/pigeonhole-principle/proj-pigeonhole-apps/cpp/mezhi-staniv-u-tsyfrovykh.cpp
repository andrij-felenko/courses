#include <iostream>
#include <vector>
#include <cstdint>

struct LcgAnalysis {
    uint32_t period;
    uint32_t pre_period;
};

LcgAnalysis analyze_lcg_period(uint32_t a, uint32_t c, uint32_t m, uint32_t seed) {
    if (m == 0) return {0, 0};

    std::vector<int> visited_at(m, -1);
    uint32_t current = seed % m;
    int step = 0;

    while (visited_at[current] == -1) {
        visited_at[current] = step;
        current = static_cast<uint32_t>((static_cast<uint64_t>(a) * current + c) % m);
        step++;
    }

    uint32_t pre = static_cast<uint32_t>(visited_at[current]);
    return LcgAnalysis{
        .period = static_cast<uint32_t>(step) - pre,
        .pre_period = pre,
    };
}

int main() {
    uint32_t a = 5, c = 3, m = 16, seed = 1;
    auto res = analyze_lcg_period(a, c, m, seed);

    std::cout << "Аналіз LCG за принципом Діріхле:\n"
              << "  Хвіст до зациклення: " << res.pre_period << "\n"
              << "  Період зациклення P: " << res.period << " (макс = " << m << ")\n";
    return 0;
}
