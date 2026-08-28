#include <vector>
#include <span>
#include <algorithm>

[[nodiscard]] double kadane_kahan_float(std::span<const double> arr) noexcept {
    if (arr.empty()) {
        return 0.0;
    }

    double current_sum = arr[0];
    double max_sum = arr[0];
    double compensation = 0.0;

    for (std::size_t i = 1; i < arr.size(); ++i) {
        if (current_sum < 0.0) {
            current_sum = arr[i];
            compensation = 0.0;
        } else {
            const double y = arr[i] - compensation;
            const double t = current_sum + y;
            compensation = (t - current_sum) - y;
            current_sum = t;
        }

        max_sum = std::max(max_sum, current_sum);
    }

    return max_sum;
}
