#include <vector>
#include <span>
#include <algorithm>
#include <numeric>

[[nodiscard]] long long kadane_circular(std::span<const int> arr) noexcept {
    if (arr.empty()) {
        return 0;
    }

    long long total_sum = arr[0];
    long long curr_max = arr[0], max_kadane = arr[0];
    long long curr_min = arr[0], min_kadane = arr[0];

    for (std::size_t i = 1; i < arr.size(); ++i) {
        const int x = arr[i];
        total_sum += x;

        curr_max = std::max<long long>(x, curr_max + x);
        max_kadane = std::max(max_kadane, curr_max);

        curr_min = std::min<long long>(x, curr_min + x);
        min_kadane = std::min(min_kadane, curr_min);
    }

    /* Якщо всі елементи від'ємні, повертаємо найкращий одиночний елемент */
    if (max_kadane < 0) {
        return max_kadane;
    }

    return std::max(max_kadane, total_sum - min_kadane);
}
