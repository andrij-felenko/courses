#include <span>
#include <functional>
#include <concepts>
#include <iterator>
#include <utility>

namespace algo {

/*
 * Наївний шаблон сортування бульбашкою для безперервного послідовного діапазону.
 *
 * @tparam T       Тип елементів. Мусить підтримувати переміщення (std::movable).
 * @tparam Compare Предикат строгого слабкого порядку. За замовчуванням std::less<T>.
 *
 * @param data     Контейнерний перегляд std::span<T>.
 * @param comp     Об'єкт функції порівняння.
 */
template <typename T, typename Compare = std::less<T>>
    requires std::strict_weak_order<Compare, T, T>
constexpr void bubble_sort_naive(std::span<T> data, Compare comp = Compare{});

/*
 * Адаптивний шаблон сортування бульбашкою з перевіркою прапорця swapped.
 *
 * @tparam T       Тип елементів.
 * @tparam Compare Предикат строгого слабкого порядку.
 *
 * @param data     Контейнерний перегляд std::span<T>.
 * @param comp     Об'єкт функції порівняння.
 */
template <typename T, typename Compare = std::less<T>>
    requires std::strict_weak_order<Compare, T, T>
constexpr void bubble_sort_adaptive(std::span<T> data, Compare comp = Compare{});

/*
 * Оптимізований шаблон сортування зі стрибком межі за індексом останнього обміну.
 *
 * @tparam T       Тип елементів.
 * @tparam Compare Предикат строгого слабкого порядку.
 *
 * @param data     Контейнерний перегляд std::span<T>.
 * @param comp     Об'єкт функції порівняння.
 */
template <typename T, typename Compare = std::less<T>>
    requires std::strict_weak_order<Compare, T, T>
constexpr void bubble_sort_last_swap(std::span<T> data, Compare comp = Compare{});

/*
 * Шаблон двонаправленого сортування перемішуванням (Cocktail Shaker Sort).
 *
 * @tparam T       Тип елементів.
 * @tparam Compare Предикат строгого слабкого порядку.
 *
 * @param data     Контейнерний перегляд std::span<T>.
 * @param comp     Об'єкт функції порівняння.
 */
template <typename T, typename Compare = std::less<T>>
    requires std::strict_weak_order<Compare, T, T>
constexpr void cocktail_shaker_sort(std::span<T> data, Compare comp = Compare{});

/*
 * Шаблон сортування для діапазонів, заданих парою ітераторів довільного доступу.
 *
 * @tparam RandomIt Ітератор випадкового доступу (std::random_access_iterator).
 * @tparam Compare  Предикат порівняння.
 *
 * @param first     Ітератор на початок діапазону.
 * @param last      Ітератор на кінець діапазону (за останнім елементом).
 * @param comp      Об'єкт функції порівняння.
 */
template <std::random_access_iterator RandomIt,
          typename Compare = std::less<typename std::iterator_traits<RandomIt>::value_type>>
constexpr void bubble_sort(RandomIt first, RandomIt last, Compare comp = Compare{});

} // namespace algo
