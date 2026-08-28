template<typename Iterator, typename Distance>
constexpr void advance(Iterator& it, Distance n) {
    using Category = typename std::iterator_traits<Iterator>::iterator_category;

    if constexpr (std::is_base_of_v<std::random_access_iterator_tag, Category>) {
        it += n;
    } else if constexpr (std::is_base_of_v<std::bidirectional_iterator_tag, Category>) {
        if (n > 0) {
            while (n--) ++it;
        } else {
            while (n++) --it;
        }
    } else {
        while (n--) {
            ++it;
        }
    }
}
