#include <algorithm>
#include <array>
#include <cstddef>
#include <cstdint>
#include <iterator>
#include <limits>

namespace viterbi {

constexpr std::size_t K   = 3;
constexpr std::size_t NU  = K - 1;             // біти пам'яті коду: тут 2
constexpr std::size_t S   = 1u << NU;          // число станів: 4
constexpr std::size_t LOW = (1u << (NU - 1)) - 1; // маска молодших ν−1 бітів стану
constexpr std::size_t D   = 10;                // глибина вікна ≈ 5·(K−1)

constexpr int INF = std::numeric_limits<int>::max();

// Ґратка коду (7,5): наступний стан і пакована пара виходів (v1<<1)|v2.
constexpr std::array<std::array<int, 2>, S> NXT = {{{0, 2}, {0, 2}, {1, 3}, {1, 3}}};
constexpr std::array<std::array<int, 2>, S> OUT = {{{0, 3}, {3, 0}, {2, 1}, {1, 2}}};

[[nodiscard]] constexpr int hamming_distance(int o, int r0, int r1) noexcept {
    return ((o >> 1) ^ r0) + ((o & 1) ^ r1);   // відстань Геммінга пари
}

struct AcsStep {
    std::array<int, S>      metrics{};
    std::array<unsigned, S> decisions{};
};

// Один такт ACS: нові метрики й один біт рішення на стан (молодший біт попередника).
[[nodiscard]] constexpr AcsStep acs(const std::array<int, S>& pm, int r0, int r1) noexcept {
    AcsStep step{};
    step.metrics.fill(INF);

    for (std::size_t s = 0; s < S; ++s) {
        if (pm[s] == INF) continue;            // у цей стан ще не дійшли
        for (int u = 0; u < 2; ++u) {
            std::size_t ns = static_cast<std::size_t>(NXT[s][u]);
            int cand = pm[s] + hamming_distance(OUT[s][u], r0, r1);
            if (cand < step.metrics[ns]) {
                step.metrics[ns]   = cand;
                step.decisions[ns] = static_cast<unsigned>(s & 1u); // переможець
            }
        }
    }
    return step;
}

[[nodiscard]] constexpr std::size_t best_state(const std::array<int, S>& m) noexcept {
    return static_cast<std::size_t>(std::distance(m.begin(), std::min_element(m.begin(), m.end())));
}

} // namespace viterbi
