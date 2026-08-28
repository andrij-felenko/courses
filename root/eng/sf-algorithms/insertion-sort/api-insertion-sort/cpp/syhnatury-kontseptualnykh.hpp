#include <iterator>
#include <ranges>
#include <functional>

namespace algo {

    /**
     * @brief Класичне сортування вставками для діапазону ітераторів.
     * Вимагає щонайменше двонаправлених ітераторів (bidirectional_iterator).
     */
    template <
        std::bidirectional_iterator I,
        std::sentinel_for<I> S,
        typename Comp = std::ranges::less,
        typename Proj = std::identity
    >
    requires std::sortable<I, Comp, Proj>
    constexpr I insertion_sort(
        I first,
        S last,
        Comp comp = {},
        Proj proj = {}
    );

    /**
     * @brief Двійкове сортування вставками.
     * Вимагає ітераторів довільного доступу (random_access_iterator) для бінарного пошуку.
     */
    template <
        std::random_access_iterator I,
        std::sentinel_for<I> S,
        typename Comp = std::ranges::less,
        typename Proj = std::identity
    >
    requires std::sortable<I, Comp, Proj>
    constexpr I binary_insertion_sort(
        I first,
        S last,
        Comp comp = {},
        Proj proj = {}
    );

    /**
     * @brief Перевантаження для безпосередньої роботи з об'єктами Range (вектори, масиви, span).
     */
    template <
        std::ranges::bidirectional_range R,
        typename Comp = std::ranges::less,
        typename Proj = std::identity
    >
    requires std::sortable<std::ranges::iterator_t<R>, Comp, Proj>
    constexpr std::ranges::borrowed_iterator_t<R> insertion_sort(
        R&& r,
        Comp comp = {},
        Proj proj = {}
    );

} // namespace algo
