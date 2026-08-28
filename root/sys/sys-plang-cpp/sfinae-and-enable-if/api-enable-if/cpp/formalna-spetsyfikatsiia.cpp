namespace std {
    // 1. Первинний шаблон для хибної умови (C++11)
    template<bool B, class T = void>
    struct enable_if {};

    // 2. Часткова спеціалізація для істинної умови (C++11)
    template<class T>
    struct enable_if<true, T> {
        using type = T;
    };

    // 3. Шаблонний псевдонім (починаючи з C++14)
    template<bool B, class T = void>
    using enable_if_t = typename enable_if<B, T>::type;
}
