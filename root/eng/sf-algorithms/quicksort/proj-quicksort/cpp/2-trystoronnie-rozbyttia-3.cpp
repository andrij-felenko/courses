#include <span>
#include <utility>
#include <functional>

template <typename T, typename Compare = std::less<T>>
void quicksort_3way(std::span<T> data, Compare comp = Compare{}) {
    if (data.size() <= 1) return;
    
    T pivot = data[0];
    size_t lt = 0;
    size_t gt = data.size() - 1;
    size_t i = 1;
    
    while (i <= gt && gt != static_cast<size_t>(-1)) {
        if (comp(data[i], pivot)) {
            std::swap(data[lt], data[i]);
            lt++;
            i++;
        } else if (comp(pivot, data[i])) {
            std::swap(data[i], data[gt]);
            gt--;
        } else {
            i++;
        }
    }
    
    if (lt > 0) {
        quicksort_3way(data.subspan(0, lt), comp);
    }
    if (gt + 1 < data.size()) {
        quicksort_3way(data.subspan(gt + 1), comp);
    }
}
