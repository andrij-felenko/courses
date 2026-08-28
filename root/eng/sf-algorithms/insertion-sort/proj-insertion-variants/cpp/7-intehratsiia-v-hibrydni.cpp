#include <span>
#include <algorithm>

/* Гібридне сортування з глобальним фінальним проходом Insertion Sort */
template <typename T, typename Compare = std::less<T>>
void hybrid_quicksort_sedgewick(std::span<T> data, Compare comp = Compare{}) {
    constexpr std::size_t threshold = 16;
    if (data.size() <= 1) {
        return;
    }

    /* Фаза 1: Рекурсивне грубе розбиття до розміру підмасивів <= threshold */
    // ... рекурсивні кроки Quicksort ...

    /* Фаза 2: Глобальний прохід сортування вставками */
    sentinel_insertion_sort(data, comp);
}
