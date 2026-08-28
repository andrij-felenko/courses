// Реалізація мовою C++: використання std::unordered_map для довільних модулів
#include <vector>
#include <span>
#include <cstdint>
#include <unordered_map>
#include <optional>

struct SubarrayRange {
    size_t start_idx;
    size_t end_idx;
};

std::optional<SubarrayRange> find_subarray_divisible_by_m(std::span<const int32_t> arr, int64_t m) {
    if (arr.empty() || m <= 0) return std::nullopt;

    // Зберігаємо перше входження кожної остачі: rem -> index
    std::unordered_map<int64_t, size_t> first_seen;
    first_seen[0] = 0; // P_0 = 0

    int64_t current_prefix = 0;
    for (size_t j = 0; j < arr.size(); ++j) {
        current_prefix += arr[j];
        
        int64_t rem = current_prefix % m;
        if (rem < 0) rem += m; // Нормалізація від'ємних остач

        if (auto it = first_seen.find(rem); it != first_seen.end()) {
            return SubarrayRange{ .start_idx = it->second, .end_idx = j };
        }
        first_seen.emplace(rem, j + 1);
    }

    return std::nullopt;
}
