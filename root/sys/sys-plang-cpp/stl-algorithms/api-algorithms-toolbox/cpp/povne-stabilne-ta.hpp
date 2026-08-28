// Стандартне сортування (Introsort)
template <class RandomIt>
void sort(RandomIt first, RandomIt last);

template <class RandomIt, class Compare>
void sort(RandomIt first, RandomIt last, Compare comp);

// Стабільне сортування (збереження відносного порядку однакових елементів)
template <class RandomIt>
void stable_sort(RandomIt first, RandomIt last);

// Часткове сортування: перші K елементів стають впорядкованими
template <class RandomIt>
void partial_sort(RandomIt first, RandomIt middle, RandomIt last);

// Пошук K-го порядкового елемента (Quickselect)
template <class RandomIt>
void nth_element(RandomIt first, RandomIt nth, RandomIt last);

// Розділення масиву на дві частини за предикатом
template <class ForwardIt, class UnaryPredicate>
ForwardIt partition(ForwardIt first, ForwardIt last, UnaryPredicate p);
