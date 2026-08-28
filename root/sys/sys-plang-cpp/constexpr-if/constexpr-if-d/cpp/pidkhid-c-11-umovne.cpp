namespace sfinae_style {

template<typename Iterator, typename Distance>
std::enable_if_t<std::is_base_of_v<std::random_access_iterator_tag, 
                 typename std::iterator_traits<Iterator>::iterator_category>>
advance(Iterator& it, Distance n) {
    it += n;
}

template<typename Iterator, typename Distance>
std::enable_if_t<std::is_base_of_v<std::bidirectional_iterator_tag, 
                 typename std::iterator_traits<Iterator>::iterator_category> &&
                !std::is_base_of_v<std::random_access_iterator_tag, 
                 typename std::iterator_traits<Iterator>::iterator_category>>
advance(Iterator& it, Distance n) {
    if (n > 0) while (n--) ++it;
    else while (n++) --it;
}

} // namespace sfinae_style
