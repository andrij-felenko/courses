#include <vector>
#include <optional>
#include <span>
#include <cstddef>

struct SubarrayIndices {
    long long max_sum{0};
    std::size_t start{0};
    std::size_t end{0};
};

[[nodiscard]] std::optional<SubarrayIndices> kadane_track_bounds(std::span<const int> arr) noexcept {
    if (arr.empty()) {
        return std::nullopt;
    }

    long long current_sum = arr[0];
    long long max_sum = arr[0];
    std::size_t current_start = 0;
    std::size_t best_start = 0;
    std::size_t best_end = 0;

    for (std::size_t i = 1; i < arr.size(); ++i) {
        if (current_sum < 0) {
            current_sum = arr[i];
            current_start = i;
        } else {
            current_sum += arr[i];
        }

        if (current_sum > max_sum) {
            max_sum = current_sum;
            best_start = current_start;
            best_end = i;
        }
    }

    return SubarrayIndices{max_sum, best_start, best_end};
}
