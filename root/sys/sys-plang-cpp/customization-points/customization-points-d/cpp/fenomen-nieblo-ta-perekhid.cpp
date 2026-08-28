namespace my_std {
    namespace __detail {
        struct __size_fn {
            template<typename T>
            constexpr auto operator()(T&& t) const {
                return t.size();
            }
        };
    }

    // Точка налаштування — це ОБ'ЄКТ, а не функція
    inline constexpr __detail::__size_fn size{};
}
