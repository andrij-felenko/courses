namespace std::ranges {
    namespace __detail {
        struct __begin_fn {
            template<typename T>
            constexpr auto operator()(T&& t) const {
                // Внутрішньо контрольовано перевіряються:
                // 1. Метод t.begin()
                // 2. ADL виклик begin(t) у закритому контексті
                // 3. Запасні варіанти для C-масивів
            }
        };
    }

    inline constexpr __detail::__begin_fn begin{};
}
