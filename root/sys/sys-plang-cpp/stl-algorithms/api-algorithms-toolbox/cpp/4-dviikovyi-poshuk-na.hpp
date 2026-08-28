// Пошук першого елемента, не меншого за значення (>=)
template <class ForwardIt, class T>
ForwardIt lower_bound(ForwardIt first, ForwardIt last, const T& value);

// Пошук першого елемента, строго більшого за значення (>)
template <class ForwardIt, class T>
ForwardIt upper_bound(ForwardIt first, ForwardIt last, const T& value);

// Отримання пари ітераторів [lower_bound, upper_bound)
template <class ForwardIt, class T>
std::pair<ForwardIt, ForwardIt> equal_range(ForwardIt first, ForwardIt last, const T& value);

// Перевірка наявності елемента
template <class ForwardIt, class T>
bool binary_search(ForwardIt first, ForwardIt last, const T& value);
