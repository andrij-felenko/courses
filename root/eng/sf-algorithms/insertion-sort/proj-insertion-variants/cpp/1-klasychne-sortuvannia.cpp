#include <span>
#include <concepts>
#include <functional>
#include <utility>

/* Ідіоматичне узагальнене сортування вставками для довільних типів та компараторів */
template <typename T, typename Compare = std::less<T>>
void insertion_sort(std::span<T> data, Compare comp = Compare{}) {
    if (data.size() <= 1) {
        return;
    }

    for (std::size_t i = 1; i < data.size(); ++i) {
        T key = std::move(data[i]);
        std::size_t j = i;

        /* Підтримуємо стійкість сортування: зсуваємо лише коли comp(key, data[j-1]) == true */
        while (j > 0 && comp(key, data[j - 1])) {
            data[j] = std::move(data[j - 1]);
            --j;
        }
        data[j] = std::move(key);
    }
}
