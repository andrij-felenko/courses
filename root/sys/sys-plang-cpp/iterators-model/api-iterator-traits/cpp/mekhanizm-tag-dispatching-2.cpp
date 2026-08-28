// Сучасна реалізація через if constexpr у C++17
template<typename It, typename Distance>
void advance(It& it, Distance n) {
    using category = typename std::iterator_traits<It>::iterator_category;
    
    if constexpr (std::is_base_of_v<std::random_access_iterator_tag, category>) {
        it += n;
    } else if constexpr (std::is_base_of_v<std::bidirectional_iterator_tag, category>) {
        if (n < 0) {
            while (n < 0) { --it; ++n; }
        } else {
            while (n > 0) { ++it; --n; }
        }
    } else {
        while (n > 0) { ++it; --n; }
    }
}
