#include <span>
#include <algorithm>
#include <functional>
#include <utility>

/* Двійкове сортування вставками з використанням стандартних алгоритмів C++ */
template <typename T, typename Compare = std::less<T>>
void binary_insertion_sort(std::span<T> data, Compare comp = Compare{}) {
    if (data.size() <= 1) {
        return;
    }

    for (auto it = data.begin() + 1; it != data.end(); ++it) {
        /* std::upper_bound гарантує вставку після дублікатів (стійкість) */
        auto insert_pos = std::upper_bound(data.begin(), it, *it, comp);

        if (insert_pos != it) {
            /* Обертання діапазону виконує зсув елементів за допомогою move-семантики */
            std::rotate(insert_pos, it, it + 1);
        }
    }
}
