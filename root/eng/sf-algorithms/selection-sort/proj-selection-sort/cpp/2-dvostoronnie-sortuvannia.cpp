#include <span>
#include <utility>
#include <functional>

namespace algo {

template <typename T, typename Compare = std::less<T>>
void double_selection_sort(std::span<T> data, Compare comp = Compare{}) {
    if (data.size() < 2) return;

    size_t left = 0;
    size_t right = data.size() - 1;

    while (left < right) {
        size_t min_idx = left;
        size_t max_idx = left;

        for (size_t i = left; i <= right; ++i) {
            if (comp(data[i], data[min_idx])) {
                min_idx = i;
            }
            if (comp(data[max_idx], data[i])) {
                max_idx = i;
            }
        }

        if (min_idx != left) {
            std::swap(data[left], data[min_idx]);
        }

        /* Пастка: якщо максимум був на позиції left, його значення зсунулося на min_idx */
        if (max_idx == left) {
            max_idx = min_idx;
        }

        if (max_idx != right) {
            std::swap(data[right], data[max_idx]);
        }

        left++;
        right--;
    }
}

} // namespace algo
