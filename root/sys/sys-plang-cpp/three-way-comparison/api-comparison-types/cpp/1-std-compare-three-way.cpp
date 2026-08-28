struct compare_three_way {
    template <class T, class U>
        requires requires(T&& t, U&& u) {
            static_cast<T&&>(t) <=> static_cast<U&&>(u);
        }
    constexpr auto operator()(T&& t, U&& u) const
        noexcept(noexcept(static_cast<T&&>(t) <=> static_cast<U&&>(u)))
        -> decltype(static_cast<T&&>(t) <=> static_cast<U&&>(u))
    {
        return static_cast<T&&>(t) <=> static_cast<U&&>(u);
    }

    using is_transparent = /*unspecified*/;
};
