// Класичне шаблонне метапрограмування C++98
template <size_t N>
struct Factorial {
    static constexpr size_t value = N * Factorial<N - 1>::value;
};

// Термінальна спеціалізація (базовий випадок рекурсії)
template <>
struct Factorial<0> {
    static constexpr size_t value = 1;
};

static_assert(Factorial<5>::value == 120);
