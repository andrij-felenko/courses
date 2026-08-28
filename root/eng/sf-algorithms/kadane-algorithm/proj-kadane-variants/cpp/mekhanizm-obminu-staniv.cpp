#include <vector>
#include <span>
#include <algorithm>

[[nodiscard]] long long max_product_subarray(std::span<const int> arr) noexcept {
    if (arr.empty()) {
        return 0;
    }

    long long max_prod = arr[0];
    long long min_prod = arr[0];
    long long global_max = arr[0];

    for (std::size_t i = 1; i < arr.size(); ++i) {
        const long long x = arr[i];

        if (x < 0) {
            std::swap(max_prod, min_prod);
        }

        max_prod = std::max(x, max_prod * x);
        min_prod = std::min(x, min_prod * x);

        global_max = std::max(global_max, max_prod);
    }

    return global_max;
}
