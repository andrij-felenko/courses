namespace std {
    // Обчислення суми всіх елементів вектору
    template <typename T, typename Abi>
    T reduce(const simd<T, Abi>& v) noexcept;

    // Горизонтальне додавання сусідніх пар елементів
    template <typename T, typename Abi>
    T hadd(const simd<T, Abi>& v) noexcept;

    // Пошук мінімального елемента серед усіх смуг вектору
    template <typename T, typename Abi>
    T hmin(const simd<T, Abi>& v) noexcept;

    // Пошук максимального елемента серед усіх смуг вектору
    template <typename T, typename Abi>
    T hmax(const simd<T, Abi>& v) noexcept;

    // Перевірка предикатів масок
    template <typename T, typename Abi>
    bool all_of(const simd_mask<T, Abi>& k) noexcept;

    template <typename T, typename Abi>
    bool any_of(const simd_mask<T, Abi>& k) noexcept;

    template <typename T, typename Abi>
    bool none_of(const simd_mask<T, Abi>& k) noexcept;
}
