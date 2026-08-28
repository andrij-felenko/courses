template <typename CostType = int64_t>
class HungarianSolver {
public:
    static AssignmentSolution<CostType> compute(
        std::span<const CostType> flat_matrix,
        int32_t rows,
        int32_t cols,
        OptimizationTarget target = OptimizationTarget::Minimize
    );
};
