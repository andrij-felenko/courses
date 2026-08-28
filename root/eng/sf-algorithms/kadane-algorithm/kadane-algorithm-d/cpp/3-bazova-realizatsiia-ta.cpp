#include <vector>
#include <span>
#include <algorithm>

[[nodiscard]] long long kadane_basic(std::span<const int> arr) noexcept {
    if (arr.empty()) {
        return 0;
    }

    long long current_sum = arr[0];
    long long max_sum = arr[0];

    for (std::size_t i = 1; i < arr.size(); ++i) {
        current_sum = std::max<long long>(arr[i], current_sum + arr[i]);
        max_sum = std::max(max_sum, current_sum);
    }

    return max_sum;
}
