#include <span>
#include <functional>
#include <concepts>
#include <iterator>

namespace algo {

/*
 * Основний шаблон сортування вибором для безперервного послідовного контейнера (std::span).
 *
 * @tparam T      Тип елементів. Мусить підтримувати переміщення або копіювання.
 * @tparam Compare Тип предикату порівняння. За замовчуванням std::less<T>.
 *
 * @param data    Перегляд масиву через std::span<T>.
 * @param comp    Об'єкт порівняння.
 */
template <typename T, typename Compare = std::less<T>>
void selection_sort(std::span<T> data, Compare comp = Compare{}) noexcept(
    noexcept(comp(data[0], data[0])) && std::is_nothrow_move_assignable_v<T>);

/*
 * Перевантаження для довільних ітераторів прямого доступу.
 *
 * @tparam RandomIt Тип ітератора (вимагає RandomAccessIterator).
 * @tparam Compare  Тип предикату порівняння.
 */
template <typename RandomIt, typename Compare = std::less<>>
void selection_sort(RandomIt first, RandomIt last, Compare comp = Compare{});

/*
 * Двостороннє сортування вибором (Min-Max Selection Sort).
 */
template <typename T, typename Compare = std::less<T>>
void double_selection_sort(std::span<T> data, Compare comp = Compare{});

/*
 * Стійке сортування вибором (Stable Selection Sort).
 */
template <typename T, typename Compare = std::less<T>>
void stable_selection_sort(std::span<T> data, Compare comp = Compare{});

} // namespace algo
