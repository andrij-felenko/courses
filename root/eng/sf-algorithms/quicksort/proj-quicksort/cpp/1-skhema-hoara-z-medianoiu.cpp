#include <vector>
#include <span>
#include <utility>
#include <functional>
#include <algorithm>

template <typename T, typename Compare = std::less<T>>
size_t median_of_three(std::span<T> data, Compare comp = Compare{}) {
    size_t lo = 0;
    size_t hi = data.size() - 1;
    size_t mid = lo + (hi - lo) / 2;
    
    if (comp(data[mid], data[lo]))  std::swap(data[lo], data[mid]);
    if (comp(data[hi], data[lo]))   std::swap(data[lo], data[hi]);
    if (comp(data[hi], data[mid]))  std::swap(data[mid], data[hi]);
    return mid;
}

template <typename T, typename Compare = std::less<T>>
size_t partition_hoare(std::span<T> data, Compare comp = Compare{}) {
    size_t pivot_idx = median_of_three(data, comp);
    T pivot = data[pivot_idx];
    
    size_t i = 0;
    size_t j = data.size() - 1;
    
    while (true) {
        while (comp(data[i], pivot)) { i++; }
        while (comp(pivot, data[j])) { j--; }
        
        if (i >= j) {
            return j;
        }
        std::swap(data[i], data[j]);
        i++;
        if (j > 0) j--;
    }
}

template <typename T, typename Compare = std::less<T>>
void quicksort_hoare(std::span<T> data, Compare comp = Compare{}) {
    while (data.size() > 1) {
        size_t p = partition_hoare(data, comp);
        
        std::span<T> left = data.subspan(0, p + 1);
        std::span<T> right = data.subspan(p + 1);
        
        /* Захист стеку: рекурсивний виклик виконується лише для меншої половини */
        if (left.size() < right.size()) {
            quicksort_hoare(left, comp);
            data = right;
        } else {
            quicksort_hoare(right, comp);
            data = left;
        }
    }
}
