// Первинний шаблон для класів-ітераторів
template<typename Iterator>
struct iterator_traits {
    using value_type = typename Iterator::value_type;
    using difference_type = typename Iterator::difference_type;
};

// Часткова спеціалізація для будь-яких вказівників T*
template<typename T>
struct iterator_traits<T*> {
    using value_type = T;
    using difference_type = std::ptrdiff_t;
};
