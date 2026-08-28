#include <iostream>
#include <vector>
#include <algorithm>
#include <span>

// Ідіоматичний C++20 варіант із використанням std::span
double jaccard_exact_sorted(std::span<const uint64_t> a, 
                            std::span<const uint64_t> b) {
    if (a.empty() && b.empty()) return 1.0;
    if (a.empty() || b.empty()) return 0.0;

    size_t i = 0, j = 0;
    size_t intersection_cnt = 0;

    while (i < a.size() && j < b.size()) {
        if (a[i] == b[j]) {
            intersection_cnt++;
            i++;
            j++;
        } else if (a[i] < b[j]) {
            i++;
        } else {
            j++;
        }
    }

    size_t union_cnt = a.size() + b.size() - intersection_cnt;
    return static_cast<double>(intersection_cnt) / static_cast<double>(union_cnt);
}
