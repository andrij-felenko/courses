namespace std {
    // 1. Первинний шаблон для хибної умови (B == false)
    template<bool B, typename T = void>
    struct enable_if {};

    // 2. Часткова спеціалізація для істинної умови (B == true)
    template<typename T>
    struct enable_if<true, T> {
        using type = T;
    };

    // 3. Допоміжний псевдонім (починаючи з C++14)
    template<bool B, typename T = void>
    using enable_if_t = typename enable_if<B, T>::type;
}
