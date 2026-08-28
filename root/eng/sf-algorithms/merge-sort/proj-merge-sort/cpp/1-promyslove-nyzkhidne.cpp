#include <iostream>
#include <vector>
#include <span>
#include <concepts>
#include <functional>
#include <utility>

namespace algorithms {

constexpr std::size_t InsertionSortThreshold = 16;

template <typename T, typename Compare = std::less<T>>
    requires std::strict_weak_order<Compare, T, T>
void insertion_sort_span(std::span<T> data, Compare comp = Compare{}) {
    const std::size_t n = data.size();
    for (std::size_t i = 1; i < n; ++i) {
        T key = std::move(data[i]);
        std::size_t j = i;
        while (j > 0 && comp(key, data[j - 1])) {
            data[j] = std::move(data[j - 1]);
            --j;
        }
        data[j] = std::move(key);
    }
}

template <typename T, typename Compare = std::less<T>>
    requires std::strict_weak_order<Compare, T, T>
void merge_top_down(std::span<T> arr, std::span<T> aux, 
                    std::size_t lo, std::size_t mid, std::size_t hi, 
                    Compare comp) {
    for (std::size_t k = lo; k <= hi; ++k) {
        aux[k] = std::move(arr[k]);
    }

    std::size_t i = lo;
    std::size_t j = mid + 1;
    std::size_t k = lo;

    while (i <= mid && j <= hi) {
        /* Збереження стійкості: comp(aux[j], aux[i]) замість <= */
        if (!comp(aux[j], aux[i])) {
            arr[k++] = std::move(aux[i++]);
        } else {
            arr[k++] = std::move(aux[j++]);
        }
    }

    while (i <= mid) {
        arr[k++] = std::move(aux[i++]);
    }
    while (j <= hi) {
        arr[k++] = std::move(aux[j++]);
    }
}

template <typename T, typename Compare = std::less<T>>
    requires std::strict_weak_order<Compare, T, T>
void merge_sort_recursive(std::span<T> arr, std::span<T> aux, 
                          std::size_t lo, std::size_t hi, 
                          Compare comp) {
    if (hi - lo + 1 <= InsertionSortThreshold) {
        insertion_sort_span(arr.subspan(lo, hi - lo + 1), comp);
        return;
    }

    const std::size_t mid = lo + (hi - lo) / 2;
    merge_sort_recursive(arr, aux, lo, mid, comp);
    merge_sort_recursive(arr, aux, mid + 1, hi, comp);

    /* Якщо стик уже впорядкований — злиття не потрібне */
    if (!comp(arr[mid + 1], arr[mid])) {
        return;
    }

    merge_top_down(arr, aux, lo, mid, hi, comp);
}

/* Публічна узагальнена функція сортування злиттям */
template <typename T, typename Compare = std::less<T>>
    requires std::strict_weak_order<Compare, T, T>
void merge_sort(std::span<T> data, Compare comp = Compare{}) {
    if (data.size() <= 1) {
        return;
    }

    std::vector<T> aux(data.size());
    merge_sort_recursive(data, std::span<T>(aux), 0, data.size() - 1, comp);
}

} // namespace algorithms
