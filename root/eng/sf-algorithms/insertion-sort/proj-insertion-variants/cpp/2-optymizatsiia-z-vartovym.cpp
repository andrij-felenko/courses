#include <span>
#include <concepts>
#include <functional>
#include <algorithm>
#include <utility>

/* Сортування з вартовим для довільних типів та ітераторів */
template <typename T, typename Compare = std::less<T>>
void sentinel_insertion_sort(std::span<T> data, Compare comp = Compare{}) {
    if (data.size() <= 1) {
        return;
    }

    /* Знаходимо мінімум та переміщуємо його на позицію data[0] */
    auto min_it = std::min_element(data.begin(), data.end(), comp);
    if (min_it != data.begin()) {
        std::iter_swap(data.begin(), min_it);
    }

    /* Основний цикл без перевірки виходу за ліву межу */
    for (std::size_t i = 2; i < data.size(); ++i) {
        T key = std::move(data[i]);
        std::size_t j = i;

        while (comp(key, data[j - 1])) {
            data[j] = std::move(data[j - 1]);
            --j;
        }
        data[j] = std::move(key);
    }
}
