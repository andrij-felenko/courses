#include <vector>
#include <numeric>
#include <cmath>
#include <iostream>

struct PartitionProblem {
    std::vector<std::int64_t> values;
    std::int64_t total_sum = 0;

    explicit PartitionProblem(std::vector<std::int64_t> vals)
        : values(std::move(vals)),
          total_sum(std::accumulate(values.begin(), values.end(), std::int64_t{0})) {}

    struct State {
        std::vector<bool> in_set1;
        std::int64_t sum1 = 0;
    };

    struct Move {
        std::size_t index = 0;
    };

    [[nodiscard]] double evaluate_full(const State& s) const noexcept {
        std::int64_t sum2 = total_sum - s.sum1;
        return static_cast<double>(std::abs(s.sum1 - sum2));
    }

    [[nodiscard]] Move propose_move(const State& /*s*/, std::mt19937_64& rng) const noexcept {
        std::uniform_int_distribution<std::size_t> dist(0, values.size() - 1);
        return Move{dist(rng)};
    }

    [[nodiscard]] double evaluate_delta(const State& s, const Move& m) const noexcept {
        std::int64_t val = values[m.index];
        std::int64_t next_sum1 = s.in_set1[m.index] ? (s.sum1 - val) : (s.sum1 + val);
        std::int64_t next_sum2 = total_sum - next_sum1;
        
        double current_energy = static_cast<double>(std::abs(s.sum1 - (total_sum - s.sum1)));
        double next_energy = static_cast<double>(std::abs(next_sum1 - next_sum2));
        return next_energy - current_energy;
    }

    void apply_move(State& s, const Move& m) const noexcept {
        std::int64_t val = values[m.index];
        if (s.in_set1[m.index]) {
            s.sum1 -= val;
            s.in_set1[m.index] = false;
        } else {
            s.sum1 += val;
            s.in_set1[m.index] = true;
        }
    }
};
