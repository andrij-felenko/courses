#include <omp.h>
#include <vector>

double computeS2Parallel(size_t n, const BonferroniSolver::IntersectionOracle& oracle) {
    double totalS2 = 0.0;

    // Паралелізація зовнішнього циклу перебору пар (i, j)
    #pragma omp parallel for reduction(+:totalS2) schedule(dynamic, 64)
    for (int64_t i = 0; i < static_cast<int64_t>(n - 1); ++i) {
        size_t pairBuf[2];
        pairBuf[0] = static_cast<size_t>(i);
        double localSum = 0.0;

        for (size_t j = i + 1; j < n; ++j) {
            pairBuf[1] = j;
            localSum += oracle(std::span<const size_t>(pairBuf, 2));
        }

        totalS2 += localSum;
    }

    return totalS2;
}
