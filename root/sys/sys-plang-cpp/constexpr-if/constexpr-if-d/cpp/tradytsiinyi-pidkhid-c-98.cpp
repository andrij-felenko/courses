namespace legacy {

template<typename RandomIt, typename Distance>
void advance_impl(RandomIt& it, Distance n, std::random_access_iterator_tag) {
    it += n; // Швидкий шлях прямого доступу O(1)
}

template<typename BiDirIt, typename Distance>
void advance_impl(BiDirIt& it, Distance n, std::bidirectional_iterator_tag) {
    if (n > 0) while (n--) ++it;
    else while (n++) --it;
}

template<typename InputIt, typename Distance>
void advance_impl(InputIt& it, Distance n, std::input_iterator_tag) {
    while (n--) ++it;
}

template<typename Iterator, typename Distance>
void advance(Iterator& it, Distance n) {
    using Category = typename std::iterator_traits<Iterator>::iterator_category;
    advance_impl(it, n, Category{}); // Створення об'єкта-тегу для вибору перевантаження
}

} // namespace legacy
