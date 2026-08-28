#include <vector>
#include <span>
#include <algorithm>

[[nodiscard]] long long kadane_branchless(std::span<const int> arr) noexcept {
    if (arr.empty()) {
        return 0;
    }

    long long current_sum = arr[0];
    long long max_sum = arr[0];

    for (std::size_t i = 1; i < arr.size(); ++i) {
        const long long x = arr[i];
        const long long prev_positive = std::max<long long>(0, current_sum);
        current_sum = prev_positive + x;
        max_sum = std::max(max_sum, current_sum);
    }

    return max_sum;
}
