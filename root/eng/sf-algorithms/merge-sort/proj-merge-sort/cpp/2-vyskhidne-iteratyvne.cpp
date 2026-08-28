#include <iostream>
#include <vector>
#include <span>
#include <algorithm>
#include <concepts>
#include <functional>

namespace algorithms {

template <typename T, typename Compare = std::less<T>>
    requires std::strict_weak_order<Compare, T, T>
void merge_blocks_iterative(std::span<const T> src, std::span<T> dst, 
                           std::size_t lo, std::size_t mid, std::size_t hi, 
                           Compare comp) {
    std::size_t i = lo;
    std::size_t j = mid;
    std::size_t k = lo;

    while (i < mid && j < hi) {
        if (!comp(src[j], src[i])) {
            dst[k++] = src[i++];
        } else {
            dst[k++] = src[j++];
        }
    }

    while (i < mid) {
        dst[k++] = src[i++];
    }
    while (j < hi) {
        dst[k++] = src[j++];
    }
}

template <typename T, typename Compare = std::less<T>>
    requires std::strict_weak_order<Compare, T, T>
void merge_sort_bottom_up(std::span<T> arr, Compare comp = Compare{}) {
    const std::size_t n = arr.size();
    if (n <= 1) {
        return;
    }

    std::vector<T> aux(n);
    std::span<T> src = arr;
    std::span<T> dst = aux;

    for (std::size_t width = 1; width < n; width *= 2) {
        for (std::size_t i = 0; i < n; i += 2 * width) {
            const std::size_t lo = i;
            const std::size_t mid = std::min(i + width, n);
            const std::size_t hi = std::min(i + 2 * width, n);
            merge_blocks_iterative<T, Compare>(src, dst, lo, mid, hi, comp);
        }

        std::swap(src, dst);
    }

    /* Якщо останній прохід записав дані у вектор aux, повертаємо їх в arr */
    if (src.data() != arr.data()) {
        std::copy(src.begin(), src.end(), arr.begin());
    }
}

} // namespace algorithms
