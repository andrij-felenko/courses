template<typename LHS, typename RHS>
concept assignable_from = 
    std::is_lvalue_reference_v<LHS> &&
    std::common_reference_with<
        const std::remove_reference_t<LHS>&,
        const std::remove_reference_t<RHS>&> &&
    requires(LHS lhs, RHS&& rhs) {
        { lhs = static_cast<RHS&&>(rhs) } -> std::same_as<LHS>;
    };

template<typename T>
concept swappable = 
    requires(T& a, T& b) {
        ranges::swap(a, b);
    };

template<typename T, typename U>
concept swappable_with = 
    std::common_reference_with<T, U> &&
    requires(T&& t, U&& u) {
        ranges::swap(static_cast<T&&>(t), static_cast<T&&>(t));
        ranges::swap(static_cast<U&&>(u), static_cast<U&&>(u));
        ranges::swap(static_cast<T&&>(t), static_cast<U&&>(u));
        ranges::swap(static_cast<U&&>(u), static_cast<T&&>(t));
    };
