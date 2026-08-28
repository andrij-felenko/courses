namespace detail {
    // Реалізація для ітераторів довільного доступу: O(1)
    template<typename RandomIt, typename Distance>
    void advance_impl(RandomIt& it, Distance n, std::random_access_iterator_tag) {
        it += n; // Одна інструкція зсуву адреси!
    }

    // Реалізація для звичайних ітераторів: O(n)
    template<typename InputIt, typename Distance>
    void advance_impl(InputIt& it, Distance n, std::input_iterator_tag) {
        while (n > 0) {
            ++it;
            --n;
        }
    }
}

template<typename It, typename Distance>
void advance(It& it, Distance n) {
    using category = typename std::iterator_traits<It>::iterator_category;
    detail::advance_impl(it, n, category{}); // Компілятор обирає потрібне перевантаження за тегом
}
