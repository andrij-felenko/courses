template<class T>
constexpr void swap(T& a, T& b)
    noexcept(is_nothrow_move_constructible_v<T> && is_nothrow_move_assignable_v<T>);
// Обмеження: is_move_constructible_v<T> && is_move_assignable_v<T>
// Дія: обмінює значення; складність — стала (три переміщення)

template<class T, size_t N>
constexpr void swap(T (&a)[N], T (&b)[N]) noexcept(is_nothrow_swappable_v<T>);
// Обмеження: is_swappable_v<T>
// Дія: як swap_ranges(a, a + N, b); складність — рівно N обмінів
