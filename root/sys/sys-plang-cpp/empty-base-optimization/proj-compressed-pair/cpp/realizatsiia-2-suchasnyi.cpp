#if defined(_MSC_VER) && !defined(__clang__)
    #define COURSES_NO_UNIQUE_ADDRESS [[msvc::no_unique_address]]
#else
    #define COURSES_NO_UNIQUE_ADDRESS [[no_unique_address]]
#endif

namespace modern {

template <typename T1, typename T2>
class compressed_pair {
    COURSES_NO_UNIQUE_ADDRESS T1 first_{};
    COURSES_NO_UNIQUE_ADDRESS T2 second_{};

public:
    compressed_pair() = default;

    template <typename U1, typename U2>
    constexpr compressed_pair(U1&& arg1, U2&& arg2)
        : first_{std::forward<U1>(arg1)},
          second_{std::forward<U2>(arg2)} {}

    template <typename... Args1, typename... Args2>
    constexpr compressed_pair(std::piecewise_construct_t,
                              std::tuple<Args1...> first_args,
                              std::tuple<Args2...> second_args)
        : first_{std::make_from_tuple<T1>(std::move(first_args))},
          second_{std::make_from_tuple<T2>(std::move(second_args))} {}

    constexpr T1& first() noexcept { return first_; }
    constexpr const T1& first() const noexcept { return first_; }

    constexpr T2& second() noexcept { return second_; }
    constexpr const T2& second() const noexcept { return second_; }
};

// Інструкції автоматичного виведення типів аргументів шаблона (CTAD)
template <typename T1, typename T2>
compressed_pair(T1, T2) -> compressed_pair<T1, T2>;

} // namespace modern
