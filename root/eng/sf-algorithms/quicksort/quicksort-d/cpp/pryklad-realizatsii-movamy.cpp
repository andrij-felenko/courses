#include <span>
#include <utility>
#include <functional>

template <typename T, typename Compare = std::less<T>>
void quicksort(std::span<T> data, Compare comp = Compare{}) {
    while (data.size() > 1) {
        size_t lo = 0;
        size_t hi = data.size() - 1;
        size_t mid = lo + (hi - lo) / 2;
        
        if (comp(data[mid], data[lo]))  std::swap(data[lo], data[mid]);
        if (comp(data[hi], data[lo]))   std::swap(data[lo], data[mid]);
        if (comp(data[hi], data[mid]))  std::swap(data[mid], data[hi]);
        
        T pivot = data[mid];
        size_t i = 0;
        size_t j = data.size() - 1;
        
        while (true) {
            while (comp(data[i], pivot)) { i++; }
            while (comp(pivot, data[j])) { j--; }
            if (i >= j) break;
            std::swap(data[i], data[j]);
            i++;
            if (j > 0) j--;
        }
        
        std::span<T> left = data.subspan(0, j + 1);
        std::span<T> right = data.subspan(j + 1);
        
        /* Захист стеку: рекурсивний виклик лише для меншого відрізка */
        if (left.size() < right.size()) {
            quicksort(left, comp);
            data = right;
        } else {
            quicksort(right, comp);
            data = left;
        }
    }
}
