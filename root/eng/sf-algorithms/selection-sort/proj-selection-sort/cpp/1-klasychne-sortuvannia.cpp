#include <span>
#include <utility>
#include <functional>
#include <concepts>

namespace algo {

/**
 * Ідіоматична C++20 реалізація сортування вибором для std::span.
 * Працює з довільними типами даних, що задовільняють концепт std::totally_ordered.
 */
template <typename T, typename Compare = std::less<T>>
void selection_sort(std::span<T> data, Compare comp = Compare{}) noexcept(
    noexcept(comp(data[0], data[0])) && std::is_nothrow_move_assignable_v<T>) 
{
    if (data.size() < 2) {
        return;
    }

    const size_t n = data.size();
    for (size_t i = 0; i < n - 1; ++i) {
        size_t min_idx = i;

        for (size_t j = i + 1; j < n; ++j) {
            if (comp(data[j], data[min_idx])) {
                min_idx = j;
            }
        }

        if (min_idx != i) {
            using std::swap;
            swap(data[i], data[min_idx]);
        }
    }
}

/**
 * Перевантаження для ітераторів довільного доступу (RandomAccessIterator).
 */
template <typename RandomIt, typename Compare = std::less<>>
void selection_sort(RandomIt first, RandomIt last, Compare comp = Compare{}) {
    if (first == last) return;

    for (auto it = first; it != last - 1; ++it) {
        auto min_it = it;
        for (auto curr = it + 1; curr != last; ++curr) {
            if (comp(*curr, *min_it)) {
                min_it = curr;
            }
        }

        if (min_it != it) {
            std::iter_swap(it, min_it);
        }
    }
}

} // namespace algo
