#include <cstdint>
#include <optional>
#include <vector>

std::optional<std::vector<long long>>
find_subset_sum(const std::vector<long long>& a, long long target) {
    int n = (int)a.size();
    for (uint64_t mask = 0; mask < (uint64_t(1) << n); ++mask) {   // усі 2ⁿ підмножин
        long long s = 0;
        for (int i = 0; i < n; ++i)
            if (mask & (uint64_t(1) << i)) s += a[i];
        if (s == target) {
            std::vector<long long> pick;
            for (int i = 0; i < n; ++i)
                if (mask & (uint64_t(1) << i)) pick.push_back(a[i]);
            return pick;
        }
    }
    return std::nullopt;                        // жодна підмножина не підійшла
}
