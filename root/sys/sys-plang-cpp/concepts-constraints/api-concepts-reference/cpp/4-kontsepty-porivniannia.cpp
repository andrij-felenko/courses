// 1. Перевірка на рівність для одного типу
template<typename T>
concept equality_comparable = 
    requires(const std::remove_reference_t<T>& a,
             const std::remove_reference_t<T>& b) {
        { a == b } -> std::convertible_to<bool>;
        { a != b } -> std::convertible_to<bool>;
    };

// 2. Двостороннє перехресне порівняння на рівність для двох різних типів
template<typename T, typename U>
concept equality_comparable_with = 
    std::equality_comparable<T> &&
    std::equality_comparable<U> &&
    std::common_reference_with<
        const std::remove_reference_t<T>&,
        const std::remove_reference_t<U>&> &&
    std::equality_comparable<
        std::common_reference_t<
            const std::remove_reference_t<T>&,
            const std::remove_reference_t<U>&>> &&
    requires(const std::remove_reference_t<T>& t,
             const std::remove_reference_t<U>& u) {
        { t == u } -> std::convertible_to<bool>;
        { t != u } -> std::convertible_to<bool>;
        { u == t } -> std::convertible_to<bool>;
        { u != t } -> std::convertible_to<bool>;
    };

// 3. Строгий повний порядок (Total Ordering)
template<typename T>
concept totally_ordered = 
    std::equality_comparable<T> &&
    requires(const std::remove_reference_t<T>& a,
             const std::remove_reference_t<T>& b) {
        { a < b }  -> std::convertible_to<bool>;
        { a > b }  -> std::convertible_to<bool>;
        { a <= b } -> std::convertible_to<bool>;
        { a >= b } -> std::convertible_to<bool>;
    };

// 4. Тристороннє порівняння через spaceship operator (<=>)
template<typename T, typename Cat = std::partial_ordering>
concept three_way_comparable = 
    requires(const std::remove_reference_t<T>& a,
             const std::remove_reference_t<T>& b) {
        { a <=> b } -> std::convertible_to<Cat>;
    };
