#include <type_traits>

template<typename T>
void analyze_type() {
    // Перевірка категорії типу
    constexpr bool is_int = std::is_integral<T>::value;
    constexpr bool is_float = std::is_floating_point<T>::value;
    constexpr bool is_ptr = std::is_pointer<T>::value;

    // Перевірка можливостей життєвого циклу
    constexpr bool is_trivially_copyable = std::is_trivially_copyable<T>::value;
    constexpr bool is_nothrow_move = std::is_nothrow_move_constructible<T>::value;
}
