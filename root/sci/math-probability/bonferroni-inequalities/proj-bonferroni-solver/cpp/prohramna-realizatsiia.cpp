#include <vector>
#include <functional>
#include <span>
#include <algorithm>
#include <stdexcept>
#include <iostream>

struct BonferroniBounds {
    double upperBound{1.0};
    double lowerBound{0.0};
    std::vector<double> sSums;
    size_t computedOrder{0};

    [[nodiscard]] double gap() const noexcept {
        return upperBound - lowerBound;
    }
};

class BonferroniSolver {
public:
    using IntersectionOracle = std::function<double(std::span<const size_t>)>;

    static BonferroniBounds compute(size_t totalEvents, size_t maxOrder, 
                                    const IntersectionOracle& oracle) {
        if (totalEvents == 0 || maxOrder == 0) {
            throw std::invalid_argument("Кількість подій та порядок повинні бути більше 0");
        }

        size_t k = std::min(maxOrder, totalEvents);
        BonferroniBounds bounds;
        bounds.sSums.resize(k + 1, 0.0);
        bounds.computedOrder = k;

        std::vector<size_t> combBuffer(k);
        double accumulator = 0.0;

        for (size_t r = 1; r <= k; ++r) {
            double sR = 0.0;
            generateCombinations(0, 0, r, totalEvents, combBuffer, sR, oracle);
            bounds.sSums[r] = sR;

            if (r % 2 == 1) {
                accumulator += sR;
                bounds.upperBound = std::min(bounds.upperBound, accumulator);
            } else {
                accumulator -= sR;
                bounds.lowerBound = std::max(bounds.lowerBound, accumulator);
            }
        }

        // Обмеження значеннями [0.0, 1.0]
        bounds.upperBound = std::clamp(bounds.upperBound, 0.0, 1.0);
        bounds.lowerBound = std::clamp(bounds.lowerBound, 0.0, bounds.upperBound);

        return bounds;
    }

private:
    static void generateCombinations(size_t startIdx, size_t depth, size_t r, 
                                     size_t n, std::vector<size_t>& currentComb, 
                                     double& sAccum, const IntersectionOracle& oracle) {
        if (depth == r) {
            sAccum += oracle(std::span<const size_t>(currentComb.data(), r));
            return;
        }

        for (size_t i = startIdx; i < n; ++i) {
            currentComb[depth] = i;
            generateCombinations(i + 1, depth + 1, r, n, currentComb, sAccum, oracle);
        }
    }
};
