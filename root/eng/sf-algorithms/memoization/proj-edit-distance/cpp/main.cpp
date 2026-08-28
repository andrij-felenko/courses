#include <string_view>
#include <vector>
#include <algorithm>

int edit_distance(std::string_view a, std::string_view b) {
    const size_t m = a.size(), n = b.size();
    std::vector<int> prev(n + 1), curr(n + 1);
    for (size_t j = 0; j <= n; ++j)
        prev[j] = static_cast<int>(j);          // рядок 0
    for (size_t i = 1; i <= m; ++i) {
        curr[0] = static_cast<int>(i);
        for (size_t j = 1; j <= n; ++j) {
            if (a[i - 1] == b[j - 1])
                curr[j] = prev[j - 1];
            else
                curr[j] = 1 + std::min({prev[j],       // згори  = видалити
                                        curr[j - 1],   // зліва  = вставити
                                        prev[j - 1]}); // діагональ = замінити
        }
        std::swap(prev, curr);                  // O(1): міняємо буфери, не копіюємо
    }
    return prev[n];
}
