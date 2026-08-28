namespace std {
    // Спеціалізація для неконстантного вказівника
    template<typename T>
    struct iterator_traits<T*> {
        using difference_type   = std::ptrdiff_t;
        using value_type        = T;
        using pointer           = T*;
        using reference         = T&;
        using iterator_category = std::random_access_iterator_tag; // у C++20: std::contiguous_iterator_tag
    };

    // Спеціалізація для константного вказівника
    template<typename T>
    struct iterator_traits<const T*> {
        using difference_type   = std::ptrdiff_t;
        using value_type        = T; // Зверніть увагу: value_type очищається від const
        using pointer           = const T*;
        using reference         = const T&;
        using iterator_category = std::random_access_iterator_tag; // у C++20: std::contiguous_iterator_tag
    };
}
