#include <string_view>
#include <span>
#include <algorithm>

struct SearchRange {
    int left{-1};
    int right{-1};
    int count{0};

    [[nodiscard]] bool found() const noexcept { return count > 0; }
};

SearchRange search_suffix_array(std::string_view text, 
                                std::span<const int> sa, 
                                std::string_view pattern) noexcept {
    SearchRange res;
    if (text.empty() || pattern.empty() || sa.empty()) return res;

    const int n = static_cast<int>(text.size());
    const int m = static_cast<int>(pattern.size());

    // 1. Пошук лівої межі
    int low = 0, high = n - 1;
    int first = -1;
    while (low <= high) {
        int mid = low + (high - low) / 2;
        std::string_view suf(text.data() + sa[mid], std::min(m, n - sa[mid]));
        if (suf >= pattern) {
            first = mid;
            high = mid - 1;
        } else {
            low = mid + 1;
        }
    }

    if (first == -1) return res;

    std::string_view found_suf(text.data() + sa[first], std::min(m, n - sa[first]));
    if (!found_suf.starts_with(pattern)) {
        return res;
    }

    // 2. Пошук правої межі
    low = first;
    high = n - 1;
    int last = first;
    while (low <= high) {
        int mid = low + (high - low) / 2;
        std::string_view suf(text.data() + sa[mid], std::min(m, n - sa[mid]));
        if (suf.starts_with(pattern)) {
            last = mid;
            low = mid + 1;
        } else if (suf < pattern) {
            low = mid + 1;
        } else {
            high = mid - 1;
        }
    }

    res.left = first;
    res.right = last;
    res.count = last - first + 1;
    return res;
}
