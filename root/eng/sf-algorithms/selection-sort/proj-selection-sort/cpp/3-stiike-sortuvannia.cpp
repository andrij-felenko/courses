#include <span>
#include <algorithm>
#include <functional>

namespace algo {

/**
 * Стійке сортування вибором мовою C++.
 * Використовує std::rotate для зсуву елементів без порушення стійкості.
 */
template <typename T, typename Compare = std::less<T>>
void stable_selection_sort(std::span<T> data, Compare comp = Compare{}) {
    if (data.size() < 2) return;

    const size_t n = data.size();
    for (size_t i = 0; i < n - 1; ++i) {
        size_t min_idx = i;

        for (size_t j = i + 1; j < n; ++j) {
            if (comp(data[j], data[min_idx])) {
                min_idx = j;
            }
        }

        if (min_idx != i) {
            /* Зсув підмасиву [i ... min_idx] праворуч так, щоб data[min_idx] став на i */
            std::rotate(data.begin() + i, data.begin() + min_idx, data.begin() + min_idx + 1);
        }
    }
}

} // namespace algo
