#include <vector>
#include <cstdint>
#include <span>
#include <limits>
#include <string_view>

enum class OptimizationTarget {
    Minimize = 0,
    Maximize = 1
};

template <typename CostType = int64_t>
struct AssignmentSolution {
    static constexpr CostType INF = std::numeric_limits<CostType>::max() / 4;

    CostType total_cost{0};
    std::vector<int32_t> assignments; // assignments[row] = col
    int32_t rows{0};
    int32_t cols{0};
};
