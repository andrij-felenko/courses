template <class T, class Cat = std::partial_ordering>
concept three_way_comparable =
    requires(const std::remove_reference_t<T>& a,
             const std::remove_reference_t<T>& b) {
        { a <=> b } -> /*compares-as*/<Cat>;
    };

template <class T, class U, class Cat = std::partial_ordering>
concept three_way_comparable_with =
    std::three_way_comparable<T, Cat> &&
    std::three_way_comparable<U, Cat> &&
    requires(const std::remove_reference_t<T>& t,
             const std::remove_reference_t<U>& u) {
        { t <=> u } -> /*compares-as*/<Cat>;
        { u <=> t } -> /*compares-as*/<Cat>;
    };
