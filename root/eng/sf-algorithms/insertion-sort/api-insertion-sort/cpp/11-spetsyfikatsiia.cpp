#include <span>
#include <functional>

template <typename T, typename Compare = std::less<T>>
void insertion_sort_subrange(std::span<T> data, std::size_t left, std::size_t right, Compare comp = Compare{}) {
    if (left >= right || right >= data.size()) {
        return;
    }
    insertion_sort(data.subspan(left, right - left + 1), comp);
}
