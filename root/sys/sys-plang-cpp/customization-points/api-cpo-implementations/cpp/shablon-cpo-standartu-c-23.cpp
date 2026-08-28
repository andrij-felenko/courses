namespace my_lib_cpp23 {
    struct __process_fn {
        // Статичний оператор виклику усуває оверхед передачі прихованого аргументу this
        template<typename T>
        static constexpr auto operator()(T&& t) noexcept(noexcept(std::forward<T>(t).process()))
            requires requires { std::forward<T>(t).process(); }
        {
            return std::forward<T>(t).process();
        }
    };

    inline constexpr __process_fn process{};
}
