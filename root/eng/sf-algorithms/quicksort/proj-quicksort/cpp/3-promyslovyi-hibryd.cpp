#include <span>
#include <algorithm>
#include <cmath>
#include <functional>

template <typename T>
void heapsort_fallback(std::span<T> data) {
    std::make_heap(data.begin(), data.end());
    std::sort_heap(data.begin(), data.end());
}

template <typename T>
void insertion_sort(std::span<T> data) {
    for (size_t i = 1; i < data.size(); ++i) {
        T key = std::move(data[i]);
        size_t j = i;
        while (j > 0 && key < data[j - 1]) {
            data[j] = std::move(data[j - 1]);
            j--;
        }
        data[j] = std::move(key);
    }
}

template <typename T>
size_t partition_lomuto(std::span<T> data) {
    T pivot = data.back();
    size_t i = 0;
    for (size_t j = 0; j < data.size() - 1; ++j) {
        if (data[j] <= pivot) {
            std::swap(data[i], data[j]);
            i++;
        }
    }
    std::swap(data[i], data.back());
    return i;
}

template <typename T>
void introsort_loop(std::span<T> data, int depth_limit) {
    while (data.size() > 16) {
        if (depth_limit == 0) {
            heapsort_fallback(data);
            return;
        }
        depth_limit--;
        size_t p = partition_lomuto(data);
        
        introsort_loop(data.subspan(p + 1), depth_limit);
        data = data.subspan(0, p);
    }
}

template <typename T>
void introsort(std::span<T> data) {
    if (data.size() < 2) return;
    int depth_limit = static_cast<int>(2 * std::log2(data.size()));
    introsort_loop(data, depth_limit);
    insertion_sort(data);
}
