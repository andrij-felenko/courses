namespace std {
    template<typename It>
    struct iterator_traits {
        using difference_type   = typename It::difference_type;
        using value_type        = typename It::value_type;
        using pointer           = typename It::pointer;
        using reference         = typename It::reference;
        using iterator_category = typename It::iterator_category;
    };
}
